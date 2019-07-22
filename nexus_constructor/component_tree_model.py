from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt
import PySide2.QtGui
from PySide2.QtGui import QVector3D
from nexus_constructor.component import Component
from nexus_constructor.transformations import Transformation, TransformationsList
from nexus_constructor.instrument import Instrument
from nexus_constructor.ui_utils import generate_unique_name


class ComponentInfo(object):
    def __init__(self, parent: Component):
        super().__init__()
        self.parent = parent


class LinkTransformation:
    def __init__(self, parent: TransformationsList):
        super().__init__()
        self.parent = parent
        self.link_transformation = None


class ComponentTreeModel(QAbstractItemModel):
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
        if issubclass(type(parent_item), Component):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        elif issubclass(type(parent_item), ComponentInfo):
            return Qt.ItemIsEnabled
        elif type(parent_item) is TransformationsList:
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
        transformation_link = LinkTransformation(transformation_list)
        transformation_list.has_link = True
        transformation_list.link = transformation_link
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
        transformation_list.link = None
        self.endRemoveRows()
        # Update depends on
        if len(transformation_list) > 0:
            parent_transform = transformation_list[len(transformation_list) - 1]
            parent_transform.depends_on = None

    def __remove_transformation(self, index: QModelIndex):
        remove_transform = index.internalPointer()
        transformation_list = remove_transform.parent
        transformation_list_index = self.parent(index)
        remove_pos = transformation_list.index(remove_transform)
        component = transformation_list.parent_component
        self.beginRemoveRows(transformation_list_index, remove_pos, remove_pos)
        component.remove_transformation(remove_transform)
        transformation_list.pop(remove_pos)
        self.endRemoveRows()

    def __remove_component(self, index: QModelIndex):
        remove_index = self.components.index(index.internalPointer())
        self.beginRemoveRows(QModelIndex(), remove_index, remove_index)
        self.instrument.remove_component(index.internalPointer())
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
            self.add_component(node_object.duplicate(self.instrument.get_component_list()))
        elif isinstance(node_object, Transformation):
            raise NotImplementedError("Duplication of transformations not implemented")

    def add_transformation(self, parent_index: QModelIndex, type: str):
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
        if type == "translation":
            new_transformation = parent_component.add_translation(
                name=generate_unique_name("Translation", transformation_list),
                vector=QVector3D(1.0, 0, 0),
            )
        elif type == "rotation":
            new_transformation = parent_component.add_rotation(
                name=generate_unique_name("Rotation", transformation_list),
                axis=QVector3D(1.0, 0, 0),
                angle=0.0,
            )
        else:
            raise ValueError("Unknown transformation type: {}".format(type))
        new_transformation.parent = transformation_list
        self.beginInsertRows(target_index, target_pos, target_pos)
        transformation_list.insert(target_pos, new_transformation)
        self.endInsertRows()
        # Update depends on
        # if target_pos == 0:
        #     parent_component.depends_on = new_transformation
        # else:
        #     parent_transform = transformation_list[target_pos]
        #     parent_transform.depends_on = new_transformation
        # if target_pos < len(transformation_list) - 1:
        #     child_transform = transformation_list[target_pos + 1]
        #     new_transformation.depends_on = child_transform
        # if target_pos == len(transformation_list) - 1 and transformation_list.has_link:
        #     new_transformation.depends_on = transformation_list.link.link_transformation

    def add_translation(self, parent_index: QModelIndex):
        self.add_transformation(parent_index, "translation")

    def add_rotation(self, parent_index: QModelIndex):
        self.add_transformation(parent_index, "rotation")

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
        elif type(parent_item) is TransformationsList:
            if parent_item.has_link and row == len(parent_item):
                return self.createIndex(row, 0, parent_item.link)
            return self.createIndex(row, 0, parent_item[row])
        raise RuntimeError("Unable to find element.")

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        parent_item = index.internalPointer()
        if type(parent_item) is Component:
            return QModelIndex()
        elif type(parent_item) is TransformationsList:
            try:
                return self.createIndex(
                    self.components.index(parent_item.parent_component),
                    0,
                    parent_item.parent_component,
                )
            except ValueError as e:
                print(e)
        elif type(parent_item) is ComponentInfo:
            return self.createIndex(
                self.components.index(parent_item.parent), 0, parent_item.parent
            )
        elif issubclass(type(parent_item), Transformation):
            return self.createIndex(1, 0, parent_item.parent)
        elif isinstance(parent_item, LinkTransformation):
            return self.createIndex(1, 0, parent_item.parent)
        raise RuntimeError("Unknown element type.")

    def rowCount(self, parent: QModelIndex) -> int:
        if not parent.isValid():
            return len(self.components)

        parent_item = parent.internalPointer()

        if type(parent_item) is Component:
            return 2
        elif type(parent_item) is TransformationsList:
            if parent_item.has_link:
                return len(parent_item) + 1
            return len(parent_item)
        elif issubclass(type(parent_item), Transformation):
            return 0
        elif type(parent_item) is ComponentInfo:
            return 0
        elif isinstance(parent_item, LinkTransformation):
            return 0
        raise RuntimeError("Unknown element type.")
