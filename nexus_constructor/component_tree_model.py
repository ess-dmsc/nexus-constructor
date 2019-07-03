#!/usr/bin/env python
from PySide2.QtCore import QAbstractItemModel, QObject
from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData
import PySide2.QtGui
from PySide2.QtGui import QVector3D
import typing
from nexus_constructor.component import ComponentModel
from nexus_constructor.transformations import TransformationModel, TransformationsList
import re

def get_duplication_name(prototype_name, list_of_nodes):
    base_name = prototype_name
    re_str = "(\((\d+)\))$"
    if re.search(re_str, prototype_name) != None:
        suffix_ctr = int(re.search(re_str, prototype_name).group(2))
        base_name = re.sub(re_str, "", prototype_name)
    else:
        suffix_ctr = 2
    base_in_use = False
    for node in list_of_nodes:
        if node.name == prototype_name:
            base_in_use = True
            break
    if not base_in_use:
        return base_name
    duplicate_name = True
    while duplicate_name:
        duplicate_name = False
        suffix = "({})".format(suffix_ctr)
        for node in list_of_nodes:
            if node.name == base_name + suffix:
                suffix_ctr += 1
                duplicate_name = True
                break
    return base_name + suffix

class ComponentInfo(object):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

class ComponentTreeModel(QAbstractItemModel):
    def __init__(self, instrument, parent=None):
        super().__init__(parent)
        self.instrument = instrument
        self.components = self.instrument.get_component_list()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item
        elif role == Qt.SizeHintRole:
            return

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        parentItem = index.internalPointer()
        if issubclass(type(parentItem), ComponentModel):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
        elif issubclass(type(parentItem), ComponentInfo):
            return Qt.ItemIsEnabled
        elif type(parentItem) is TransformationsList:
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled


    def mimeData(self, indexes: typing.List[int]) -> PySide2.QtCore.QMimeData:
        mimeData = QMimeData()
        mimeData.setData("test_type", bytearray("no_mime".encode("utf8")))
        mimeData.data_pointers = []
        for itm in indexes:
            mimeData.data_pointers.append(itm.internalPointer())
        return mimeData

    def mimeTypes(self):
        return ["test_type"]

    def supportedDropActions(self) -> PySide2.QtCore.Qt.DropActions:
        return Qt.DropAction.MoveAction

    def dropMimeData(self, data: PySide2.QtCore.QMimeData, action: PySide2.QtCore.Qt.DropAction, row: int, column: int, parent: PySide2.QtCore.QModelIndex):
        TgtNode = parent.internalPointer()
        if type(TgtNode) is list:
            for i in range(len(data.data_pointers)):
                cData = data.data_pointers[i]
                oldDataParent = cData.parentItem
                oldDataParent.childItems.remove(cData)
                cData.parentItem = TgtNode
                if (row >= 0):
                    TgtNode.childItems.insert(row, cData)
                else:
                    TgtNode.childItems.append(cData)
                self.dataChanged.emit(QModelIndex(), QModelIndex())
                self.layoutChanged.emit()
                return True
        return False

    def add_component(self, new_component):
        self.beginInsertRows(QModelIndex(), len(self.components), len(self.components))
        self.components.append(new_component)
        self.endInsertRows()

    def remove_node(self, node):
        if isinstance(node.internalPointer(), ComponentModel):
            remove_index = self.components.index(node.internalPointer())
            self.beginRemoveRows(QModelIndex(), remove_index, remove_index)
            self.instrument.remove_component(node.internalPointer())
            self.components.pop(remove_index)
            self.endRemoveRows()
        elif isinstance(node.internalPointer(), TransformationModel):
            transformation_list = node.internalPointer().parent
            transformation_list_index = self.parent(node)
            remove_pos = transformation_list.index(node.internalPointer())
            component = transformation_list.parent_component
            self.beginRemoveRows(transformation_list_index, remove_pos, remove_pos)
            component.remove_transformation(node.internalPointer())
            transformation_list.pop(remove_pos)
            self.endRemoveRows()

    def duplicate_node(self, node):
        parent = node.internalPointer()
        if isinstance(parent, ComponentModel):
            new_name = get_duplication_name(parent.name, self.components)

            self.add_component(self.instrument.add_component(new_name, parent.nx_class, parent.description))
        elif isinstance(parent, TransformationModel):
            raise NotImplementedError("Duplication of transformations not implemented")

    def add_translation(self, parent_index):
        parentItem = parent_index.internalPointer()
        transformation_list = None
        parent_component = None
        target_pos = 0
        target_index = QModelIndex()
        if isinstance(parentItem, ComponentModel):
            transformation_list = parentItem.stored_transforms
            parent_component = parentItem
            target_pos = len(transformation_list)
            target_index = self.index(1, 0, parent_index)
        elif isinstance(parentItem, TransformationsList):
            transformation_list = parentItem
            parent_component = parentItem.parent_component
            target_pos = len(transformation_list)
            target_index = parent_index
        elif isinstance(parentItem, TransformationModel):
            transformation_list = parentItem.parent
            parent_component = transformation_list.parent_component
            target_pos = transformation_list.index(parentItem) + 1
            target_index = self.parent(parent_index)
        new_transformation = parent_component.add_translation(name = get_duplication_name("Translation", transformation_list), vector = QVector3D(1.0, 0, 0))
        new_transformation.parent = transformation_list
        self.beginInsertRows(target_index, target_pos, target_pos)
        transformation_list.insert(target_pos, new_transformation)
        self.endInsertRows()

    def add_rotation(self, parent):
        pass

    def dropEvent(self, event: PySide2.QtGui.QDropEvent):
        print("Done dropping")

    def headerData(self, section, orientation, role):
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, 0, self.components[row])

        parentItem = parent.internalPointer()

        if isinstance(parentItem, ComponentModel):
            if row == 0:
                if not hasattr(parentItem, "component_info"):
                    parentItem.component_info = ComponentInfo(parentItem)
                return self.createIndex(0, 0, parentItem.component_info)
            elif row == 1:
                if not hasattr(parentItem, "stored_transforms"):
                    parentItem.stored_transforms = parentItem.transforms
                return self.createIndex(1, 0, parentItem.stored_transforms)
            else:
                return QModelIndex()
        elif type(parentItem) is TransformationsList:
            return self.createIndex(row, 0, parentItem[row])

        #
        # if type(parentItem) is list or type(parentItem) is Cp.TransformationList:
        #     childItem = parentItem[row]
        # elif issubclass(type(parentItem), Cp.Component):
        #     childItem = parentItem.transformations
        # if childItem is not None:
        #     return self.createIndex(row, column, childItem)
        raise RuntimeError("Unable to find element.")

    def parent(self, index):
        # list.index uses the comparison operator to find an item but we want to find the actual object (pointer)
        # is there a simple pythonic way to fix this or should we add some attribute to make sure that every
        # item is unique?
        if not index.isValid():
            return QModelIndex()
        parentItem = index.internalPointer()
        if type(parentItem) is ComponentModel:
            return QModelIndex()
        elif type(parentItem) is TransformationsList:
            try:
                return self.createIndex(self.components.index(parentItem.parent_component), 0, parentItem.parent_component)
            except ValueError as e:
                print(e)
        elif type(parentItem) is ComponentInfo:
            return self.createIndex(self.components.index(parentItem.parent), 0, parentItem.parent)
        elif issubclass(type(parentItem), TransformationModel):
            return self.createIndex(1, 0, parentItem.parent)
        raise RuntimeError("Unknown element type.")

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.components)

        parentItem = parent.internalPointer()

        if type(parentItem) is ComponentModel:
            return 2
        elif type(parentItem) is TransformationsList:
            return len(parentItem)
        elif issubclass(type(parentItem), TransformationModel):
            return 0
        elif type(parentItem) is ComponentInfo:
            return 0
        raise RuntimeError("Unknown element type.")