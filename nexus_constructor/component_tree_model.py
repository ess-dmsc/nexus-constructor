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

class LinkTransformation:
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.link_transformation = None

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
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        elif issubclass(type(parentItem), ComponentInfo):
            return Qt.ItemIsEnabled
        elif type(parentItem) is TransformationsList:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def supportedDropActions(self) -> PySide2.QtCore.Qt.DropActions:
        return Qt.DropAction.MoveAction

    def add_link(self, node):
        parentItem = node.internalPointer()
        transformation_list = None
        target_index = QModelIndex()
        if isinstance(parentItem, ComponentModel):
            if not hasattr(parentItem, "stored_transforms"):
                parentItem.stored_transforms = parentItem.transforms
            transformation_list = parentItem.stored_transforms
            target_index = self.index(1, 0, node)
        elif isinstance(parentItem, TransformationsList):
            transformation_list = parentItem
            target_index = node
        elif isinstance(parentItem, TransformationModel):
            transformation_list = parentItem.parent
            target_index = self.parent(node)
        if transformation_list.has_link:
            return
        target_pos = len(transformation_list)
        self.beginInsertRows(target_index, target_pos, target_pos)
        transformation_link = LinkTransformation(transformation_list)
        transformation_list.has_link = True
        transformation_list.link = transformation_link
        self.endInsertRows()

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
        elif isinstance(node.internalPointer(), LinkTransformation):
            transformation_list = node.internalPointer().parent
            transformation_list_index = self.parent(node)
            remove_pos = len(transformation_list)
            self.beginRemoveRows(transformation_list_index, remove_pos, remove_pos)
            transformation_list.has_link = False
            transformation_list.link = None
            self.endRemoveRows()
            #Update depends on
            if len(transformation_list) > 0:
                parent_transform = transformation_list[len(transformation_list) - 1]
                parent_transform.depends_on = None

    def duplicate_node(self, node):
        parent = node.internalPointer()
        if isinstance(parent, ComponentModel):
            new_name = get_duplication_name(parent.name, self.components)

            self.add_component(self.instrument.add_component(new_name, parent.nx_class, parent.description))
        elif isinstance(parent, TransformationModel):
            raise NotImplementedError("Duplication of transformations not implemented")

    def add_transformation(self, parent_index, type):
        parentItem = parent_index.internalPointer()
        transformation_list = None
        parent_component = None
        target_pos = 0
        target_index = QModelIndex()
        if isinstance(parentItem, ComponentModel):
            if not hasattr(parentItem, "stored_transforms"):
                parentItem.stored_transforms = parentItem.transforms
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
        if type == "translation":
            new_transformation = parent_component.add_translation(
                name=get_duplication_name("Translation", transformation_list), vector=QVector3D(1.0, 0, 0))
        elif type == "rotation":
            new_transformation = parent_component.add_rotation(
                name=get_duplication_name("Rotation", transformation_list), axis=QVector3D(1.0, 0, 0), angle = 0.0)
        else:
            raise ValueError("Unknown transformation type: {}".format(type))
        new_transformation.parent = transformation_list
        self.beginInsertRows(target_index, target_pos, target_pos)
        transformation_list.insert(target_pos, new_transformation)
        self.endInsertRows()
        # Update depends on
        if target_pos == 0:
            parent_component.depends_on = new_transformation
        else:
            parent_transform = transformation_list[target_pos]
            parent_transform.depends_on = new_transformation
        if target_pos < len(transformation_list) - 1:
            child_transform = transformation_list[target_pos + 1]
            new_transformation.depends_on = child_transform
        if target_pos == len(transformation_list) - 1 and transformation_list.has_link:
            new_transformation.depends_on = transformation_list.link.link_transformation
    
    def add_translation(self, parent_index):
        self.add_transformation(parent_index, "translation")

    def add_rotation(self, parent_index):
        self.add_transformation(parent_index, "rotation")

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
            if parentItem.has_link and row == len(parentItem):
                return self.createIndex(row,  0, parentItem.link)
            return self.createIndex(row, 0, parentItem[row])
        raise RuntimeError("Unable to find element.")

    def parent(self, index):
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
        elif isinstance(parentItem, LinkTransformation):
            return self.createIndex(1, 0, parentItem.parent)
        raise RuntimeError("Unknown element type.")

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.components)

        parentItem = parent.internalPointer()

        if type(parentItem) is ComponentModel:
            return 2
        elif type(parentItem) is TransformationsList:
            if parentItem.has_link:
                return len(parentItem) + 1
            return len(parentItem)
        elif issubclass(type(parentItem), TransformationModel):
            return 0
        elif type(parentItem) is ComponentInfo:
            return 0
        elif isinstance(parentItem, LinkTransformation):
            return 0
        raise RuntimeError("Unknown element type.")