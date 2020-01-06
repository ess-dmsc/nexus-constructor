from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal
import PySide2.QtGui
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QMessageBox

from nexus_constructor.component.component import Component
from nexus_constructor.component.transformations_list import TransformationsList
from nexus_constructor.component.link_transformation import LinkTransformation
from nexus_constructor.transformation_types import TransformationType

from nexus_constructor.transformations import Transformation
import logging

from nexus_constructor.instrument import Instrument
from nexus_constructor.ui_utils import generate_unique_name


class ComponentInfo(object):
    def __init__(self, parent: Component):
        super().__init__()
        self.parent = parent


class ComponentTreeModel(QAbstractItemModel):
    data_changed = Signal("QModelIndex", "QModelIndex")

    def __init__(self, instrument: Instrument, parent=None):
        super().__init__(parent)
        self.instrument = instrument
        self.components = self.instrument.get_component_list()

    def columnCount(self, parent: QModelIndex) -> int:
        return 1

    def data(self, index: QModelIndex, role: Qt.DisplayRole):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item
        elif role == Qt.SizeHintRole:
            return

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        parent_item = index.internalPointer()
        if isinstance(parent_item, Component):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        elif isinstance(parent_item, ComponentInfo):
            return Qt.ItemIsEnabled
        elif isinstance(parent_item, TransformationsList):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def supportedDropActions(self) -> PySide2.QtCore.Qt.DropActions:
        return Qt.DropAction.MoveAction

    def add_link(self, node: QModelIndex):
        parent_item = node.internalPointer()
        transformation_list = None
        target_index = QModelIndex()
        if isinstance(parent_item, Component):
            if not hasattr(parent_item, "stored_transforms"):
                parent_item.stored_transforms = parent_item.transforms
            transformation_list = parent_item.stored_transforms
            target_index = self.index(1, 0, node)
        elif isinstance(parent_item, TransformationsList):
            transformation_list = parent_item
            target_index = node
        elif isinstance(parent_item, Transformation):
            transformation_list = parent_item.parent
            target_index = self.parent(node)
        if transformation_list.has_link:
            return
        target_pos = len(transformation_list)
        self.beginInsertRows(target_index, target_pos, target_pos)
        transformation_list.has_link = True
        self.endInsertRows()

    def add_component(self, new_component: Component):
        self.beginInsertRows(QModelIndex(), len(self.components), len(self.components))
        self.components.append(new_component)
        self.endInsertRows()

    def __remove_link(self, index: QModelIndex):
        transformation_list = index.internalPointer().parent
        transformation_list_index = self.parent(index)
        remove_pos = len(transformation_list)
        self.beginRemoveRows(transformation_list_index, remove_pos, remove_pos)
        transformation_list.has_link = False
        self.endRemoveRows()
        # Update depends on
        if len(transformation_list) > 0:
            parent_transform = transformation_list[len(transformation_list) - 1]
            parent_transform.depends_on = None

    def __update_link_rows(self):
        nr_of_components = self.rowCount(QModelIndex())
        for i in range(nr_of_components):
            component_index = self.index(i, 0, QModelIndex())
            transformations_index = self.index(1, 0, component_index)
            transformations = transformations_index.internalPointer()
            if transformations.has_link:
                transformation_rows = self.rowCount(transformations_index)
                link_index = self.index(
                    transformation_rows - 1, 0, transformations_index
                )
                self.dataChanged.emit(link_index, link_index)

    def __remove_transformation(self, index: QModelIndex):
        remove_transform = index.internalPointer()
        transformation_list = remove_transform.parent
        transformation_list_index = self.parent(index)
        remove_pos = transformation_list.index(remove_transform)
        component = transformation_list.parent_component

        remove_transform.remove_from_dependee_chain()
        self.__update_link_rows()

        self.beginRemoveRows(transformation_list_index, remove_pos, remove_pos)
        component.remove_transformation(remove_transform)
        transformation_list.pop(remove_pos)
        self.endRemoveRows()
        self.instrument.nexus.transformation_changed.emit()

    def __remove_component(self, index: QModelIndex):
        component = index.internalPointer()
        transforms = component.transforms
        if transforms and transforms[0].get_dependents():
            reply = QMessageBox.question(
                None,
                "Delete component?",
                "this component has transformations that are depended on. Are you sure you want to delete it?",
                QMessageBox.Yes,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                pass
            elif reply == QMessageBox.No:
                return
        remove_index = self.components.index(index.internalPointer())
        self.beginRemoveRows(QModelIndex(), remove_index, remove_index)
        for transform in transforms:
            transform.remove_from_dependee_chain()
        self.instrument.remove_component(component)
        self.components.pop(remove_index)
        self.endRemoveRows()

    def remove_node(self, node: QModelIndex):
        if isinstance(node.internalPointer(), Component):
            self.__remove_component(node)
        elif isinstance(node.internalPointer(), Transformation):
            self.__remove_transformation(node)
        elif isinstance(node.internalPointer(), LinkTransformation):
            self.__remove_link(node)

    def duplicate_node(self, node: QModelIndex):
        node_object = node.internalPointer()
        if isinstance(node_object, Component):
            self.add_component(
                node_object.duplicate(self.instrument.get_component_list())
            )
        elif isinstance(node_object, Transformation):
            raise NotImplementedError("Duplication of transformations not implemented")

    def add_transformation(
        self, parent_index: QModelIndex, transformation_type: TransformationType
    ):
        parent_item = parent_index.internalPointer()
        transformation_list = None
        parent_component = None
        target_pos = 0
        target_index = QModelIndex()
        if isinstance(parent_item, Component):
            if not hasattr(parent_item, "stored_transforms"):
                parent_item.stored_transforms = parent_item.transforms
            transformation_list = parent_item.stored_transforms
            parent_component = parent_item
            target_pos = len(transformation_list)
            target_index = self.index(1, 0, parent_index)
        elif isinstance(parent_item, TransformationsList):
            transformation_list = parent_item
            parent_component = parent_item.parent_component
            target_pos = len(transformation_list)
            target_index = parent_index
        elif isinstance(parent_item, Transformation):
            transformation_list = parent_item.parent
            parent_component = transformation_list.parent_component
            target_pos = transformation_list.index(parent_item) + 1
            target_index = self.parent(parent_index)
        if transformation_type == TransformationType.TRANSLATION:
            new_transformation = parent_component.add_translation(
                name=generate_unique_name(
                    TransformationType.TRANSLATION.value, transformation_list
                ),
                vector=QVector3D(1.0, 0, 0),
            )
        elif transformation_type == TransformationType.ROTATION:
            new_transformation = parent_component.add_rotation(
                name=generate_unique_name("Rotation", transformation_list),
                axis=QVector3D(1.0, 0, 0),
                angle=0.0,
            )
        else:
            raise ValueError(f"Unknown transformation type: {transformation_type}")
        new_transformation.parent = transformation_list
        self.beginInsertRows(target_index, target_pos, target_pos)
        transformation_list.insert(target_pos, new_transformation)
        self.endInsertRows()
        parent_component.depends_on = transformation_list[0]
        linked_component = None
        if transformation_list.has_link:
            linked_component = transformation_list.link.linked_component
        for i in range(len(transformation_list) - 1):
            transformation_list[i].depends_on = transformation_list[i + 1]
        if transformation_list.has_link:
            transformation_list.link.linked_component = linked_component
            if linked_component is not None:
                transformation_list[
                    -1
                ].depends_on = transformation_list.link.linked_component.transforms[0]
        self.instrument.nexus.transformation_changed.emit()

    def add_translation(self, parent_index: QModelIndex):
        self.add_transformation(parent_index, TransformationType.TRANSLATION)

    def add_rotation(self, parent_index: QModelIndex):
        self.add_transformation(parent_index, TransformationType.ROTATION)

    def headerData(self, section, orientation, role):
        return None

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, 0, self.components[row])

        parent_item = parent.internalPointer()

        if isinstance(parent_item, Component):
            if row == 0:
                if not hasattr(parent_item, "component_info"):
                    parent_item.component_info = ComponentInfo(parent_item)
                return self.createIndex(0, 0, parent_item.component_info)
            elif row == 1:
                if not hasattr(parent_item, "stored_transforms"):
                    parent_item.stored_transforms = parent_item.transforms
                return self.createIndex(1, 0, parent_item.stored_transforms)
            else:
                return QModelIndex()
        elif isinstance(parent_item, TransformationsList):
            if parent_item.has_link and row == len(parent_item):
                return self.createIndex(row, 0, parent_item.link)
            return self.createIndex(row, 0, parent_item[row])
        raise RuntimeError("Unable to find element.")

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        parent_item = index.internalPointer()
        if isinstance(parent_item, Component):
            return QModelIndex()
        elif isinstance(parent_item, TransformationsList):
            try:
                return self.createIndex(
                    self.components.index(parent_item.parent_component),
                    0,
                    parent_item.parent_component,
                )
            except ValueError as e:
                logging.error(e)
        elif isinstance(parent_item, ComponentInfo):
            return self.createIndex(
                self.components.index(parent_item.parent), 0, parent_item.parent
            )
        elif isinstance(parent_item, Transformation):
            return self.createIndex(1, 0, parent_item.parent)
        elif isinstance(parent_item, LinkTransformation):
            return self.createIndex(1, 0, parent_item.parent)
        raise RuntimeError("Unknown element type.")

    def rowCount(self, parent: QModelIndex) -> int:
        if not parent.isValid():
            return len(self.components)

        parent_item = parent.internalPointer()

        if isinstance(parent_item, Component):
            return 2
        elif isinstance(parent_item, TransformationsList):
            if parent_item.has_link:
                return len(parent_item) + 1
            return len(parent_item)
        elif isinstance(parent_item, Transformation):
            return 0
        elif isinstance(parent_item, ComponentInfo):
            return 0
        elif isinstance(parent_item, LinkTransformation):
            return 0
        raise RuntimeError("Unknown element type.")
