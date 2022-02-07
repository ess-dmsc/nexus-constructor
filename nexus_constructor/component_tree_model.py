from typing import Optional, Tuple, Union

import PySide2.QtGui
from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QMessageBox

from nexus_constructor.common_attrs import TRANSFORMATIONS, TransformationType
from nexus_constructor.link_transformation import LinkTransformation
from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import Dataset, FileWriterModule
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.model.value_type import ValueTypes
from nexus_constructor.transformations_list import TransformationsList
from nexus_constructor.ui_utils import generate_unique_name


class ComponentInfo(object):
    def __init__(self, parent: Component):
        super().__init__()
        self.parent = parent


class NexusTreeModel(QAbstractItemModel):
    def __init__(self, model: Model, parent=None):
        super().__init__(parent)
        self.model = model
        self.components = self.model.get_components()
        self.tree_root = self.model.entry
        self.current_nxs_obj: Optional[
            Tuple[Union[Group, FileWriterModule], QModelIndex]
        ] = (self.model.entry, None)

    def columnCount(self, parent: QModelIndex) -> int:
        return 1

    def parent(self, index: QModelIndex):
        if index.isValid():
            parent_item = index.internalPointer().parent_node
            if parent_item:
                return self.createIndex(index.row(), 0, parent_item)
        return QModelIndex()

    def data(self, index: QModelIndex, role: Qt.DisplayRole):
        if not index.isValid():
            return None
        item = index.internalPointer()
        self.current_nxs_obj = (item, index)
        if role == Qt.DisplayRole:
            return item
        elif role == Qt.SizeHintRole:
            return

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            return self.createIndex(row, column, self.tree_root)
        parent_item = parent.internalPointer()
        index = self.createIndex(row, column, parent_item.children[row])
        self.current_nxs_obj = (parent_item.children[row], index)
        return index

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        parent_item = index.internalPointer()
        if isinstance(parent_item, (Component, TransformationsList)):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        elif isinstance(parent_item, ComponentInfo):
            return Qt.ItemIsEnabled
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def supportedDropActions(self) -> PySide2.QtCore.Qt.DropActions:
        return Qt.DropAction.MoveAction

    def rowCount(self, parent: QModelIndex) -> int:
        if not parent.isValid():
            return 1
        else:
            node = parent.internalPointer()
            if isinstance(node, Group):
                return node.number_of_children()
            else:
                return 0

    def add_group(self, new_group: Group):
        parent_node, _ = self.current_nxs_obj
        if not isinstance(parent_node, Group):
            parent_node = parent_node.parent_node
        pointer = self.createIndex(parent_node.number_of_children(), 0, parent_node)
        self.beginInsertRows(
            pointer, parent_node.number_of_children(), parent_node.number_of_children()
        )
        if isinstance(new_group, Component):
            self.components.append(new_group)
        parent_node[new_group.name] = new_group
        self.endInsertRows()

    @staticmethod
    def _get_row_of_child(row_child):
        if not row_child.parent_node:
            return -1
        for c, child in enumerate(row_child.parent_node.children):
            if row_child == child:
                return c
        return -1

    def add_module(self, new_module: FileWriterModule, component):

        parent_node = component
        pointer = self.createIndex(parent_node.number_of_children(), 0, parent_node)
        self.beginInsertRows(
            pointer, parent_node.number_of_children(), parent_node.number_of_children()
        )
        parent_node.children.append(new_module)
        self.endInsertRows()

    def headerData(self, section, orientation, role):
        return None

    def add_link(self, node: QModelIndex):
        parent_item = node.internalPointer()

        target_index, transformation_list = self._get_transformation_list(
            node, parent_item
        )
        if transformation_list.has_link:
            return
        target_pos = len(transformation_list)
        self.beginInsertRows(target_index, target_pos, target_pos)
        transformation_list.has_link = True
        self.endInsertRows()

    def add_transformation(self, parent_index: QModelIndex, transformation_type: str):
        parent_item = parent_index.internalPointer()
        transformation_list = None
        parent_component = None
        target_pos = 0
        target_index = QModelIndex()
        (
            parent_component,
            target_index,
            target_pos,
            transformation_list,
        ) = self._get_target_position(
            parent_component,
            parent_index,
            parent_item,
            target_index,
            target_pos,
            transformation_list,
        )
        new_transformation = self._create_new_transformation(
            parent_component, transformation_list, transformation_type
        )

        new_transformation.parent_component = parent_component
        self.beginInsertRows(
            target_index,
            parent_component.number_of_children(),
            parent_component.number_of_children(),
        )
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
        self.model.signals.transformation_changed.emit()

    def add_translation(self, parent_index: QModelIndex):
        self.add_transformation(parent_index, TransformationType.TRANSLATION)

    def add_rotation(self, parent_index: QModelIndex):
        self.add_transformation(parent_index, TransformationType.ROTATION)

    def _get_target_position(
        self,
        parent_component,
        parent_index,
        parent_item,
        target_index,
        target_pos,
        transformation_list,
    ):
        """
        :param parent_component: component to add transformation to
        :param parent_index: index of the parent_item
        :param parent_item: the component, transformation list or transformation that was selected "add" button pressed
        :param target_index: index of parent component of new transformation
        :param target_pos: position for new transformation in transformation list
        :param transformation_list: transformation list of parent_component
        """
        if isinstance(parent_item, Component):
            if parent_item.stored_transforms is None:
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
            transformation_list = parent_item.parent_component.stored_transforms
            parent_component = transformation_list.parent_component
            target_pos = transformation_list.index(parent_item) + 1
            target_index = self.parent(parent_index)
        return parent_component, target_index, target_pos, transformation_list

    def _get_transformation_list(self, node, parent_item):
        transformation_list = None
        target_index = QModelIndex()
        if isinstance(parent_item, Component):
            transformation_list = parent_item.transforms
            target_index = self.index(1, 0, node)
        elif isinstance(parent_item, TransformationsList):
            transformation_list = parent_item
            target_index = node
        elif isinstance(parent_item, Transformation):
            transformation_list = parent_item.parent_component.transforms
            target_index = self.parent(node)
        return target_index, transformation_list

    @staticmethod
    def _create_new_transformation(
        parent_component, transformation_list, transformation_type
    ):
        values = Dataset(
            parent_node=parent_component, name="", type=ValueTypes.DOUBLE, values=""
        )
        if transformation_type == TransformationType.TRANSLATION:
            new_transformation = parent_component.add_translation(
                name=generate_unique_name(
                    TransformationType.TRANSLATION, transformation_list
                ),
                vector=QVector3D(0, 0, 1.0),  # default to beam direction
                values=values,
            )
        elif transformation_type == TransformationType.ROTATION:
            new_transformation = parent_component.add_rotation(
                name=generate_unique_name(
                    TransformationType.ROTATION, transformation_list
                ),
                axis=QVector3D(1.0, 0, 0),
                angle=0.0,
                values=values,
            )
        else:
            raise ValueError(f"Unknown transformation type: {transformation_type}")
        return new_transformation

    def remove_node(self, node: QModelIndex):
        nexus_object = node.internalPointer()
        if isinstance(nexus_object, Transformation):
            self._remove_transformation(node)
        if isinstance(nexus_object, Group):
            if nexus_object.name == TRANSFORMATIONS:
                for transform in nexus_object.parent_node.transforms:  # type: ignore
                    transform.remove_from_dependee_chain()
                nexus_object.parent_node.stored_transforms = None  # type: ignore
                self.model.signals.transformation_changed.emit()
            self._remove_component(node)
        elif isinstance(nexus_object, LinkTransformation):
            self._remove_link(node)

    def _remove_component(self, index: QModelIndex):
        component = index.internalPointer()
        transforms = []  # type: ignore
        if isinstance(component, Component):
            transforms = component.transforms
        if transforms:
            has_dependents_other_than_the_component_being_deleted = (
                len(transforms[0].dependents) > 1
            )
            if has_dependents_other_than_the_component_being_deleted:
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
        parent_index = QModelIndex()
        if index.internalPointer().parent_node:
            row = self._get_row_of_child(index.internalPointer().parent_node)
            if not row < 0:
                parent_index = self.createIndex(
                    row, 0, index.internalPointer().parent_node
                )
        remove_index = self._get_row_of_child(index.internalPointer())
        self.beginRemoveRows(parent_index, remove_index, remove_index)
        for transform in transforms:
            transform.remove_from_dependee_chain()
        if isinstance(component, Component) and component.name in [
            c.name for c in self.components
        ]:
            self.components.remove(component)
        del component.parent_node[component.name]
        self.endRemoveRows()
        if component.name != TRANSFORMATIONS:
            self.model.signals.component_removed.emit(component.name)

    def _remove_transformation(self, index: QModelIndex):
        remove_transform = index.internalPointer()
        transformation_list = remove_transform.parent_component.stored_transforms
        transformation_list_index = self.parent(index)
        remove_pos = transformation_list.index(remove_transform)
        component = transformation_list.parent_component

        remove_transform.remove_from_dependee_chain()
        self.__update_link_rows()

        self.beginRemoveRows(transformation_list_index, remove_pos, remove_pos)
        component.remove_transformation(remove_transform)
        transformation_list.pop(remove_pos)
        self.endRemoveRows()
        self.model.signals.transformation_changed.emit()

    def _remove_link(self, index: QModelIndex):
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
        self.model.signals.transformation_changed.emit()

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
