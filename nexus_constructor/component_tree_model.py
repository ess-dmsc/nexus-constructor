#!/usr/bin/env python
from PySide2.QtCore import QAbstractItemModel, QObject
from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData
import PySide2.QtGui
import typing
from nexus_constructor.component import ComponentModel
from nexus_constructor.transformations import TransformationModel, TransformationsList

class ComponentInfo(object):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

class ComponentTreeModel(QAbstractItemModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.rootItem = data

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

    def updateModel(self):
        self.dataChanged.emit(QModelIndex(), QModelIndex())
        self.layoutChanged.emit()

    def dropEvent(self, event: PySide2.QtGui.QDropEvent):
        print("Done dropping")

    def headerData(self, section, orientation, role):
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, 0, self.rootItem[row])

        parentItem = parent.internalPointer()

        if isinstance(parentItem) is ComponentModel:
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
            row = self.rootItem.index(parentItem.parent_component)
            parent = parentItem.parent_component
            return self.createIndex(row, 0, parent)
        elif type(parentItem) is ComponentInfo:
            return self.createIndex(self.rootItem.index(parentItem.parent), 0, parentItem.parent)
        elif issubclass(type(parentItem), TransformationModel):
            return self.createIndex(1, 0, parentItem.parent)
        raise RuntimeError("Unknown element type.")

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.rootItem)

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