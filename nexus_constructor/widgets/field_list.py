from PySide2.QtWidgets import QListView, QWidget, QLabel, QStyledItemDelegate, QLineEdit, QStyleOptionViewItem, QVBoxLayout
from PySide2.QtCore import QAbstractListModel, QModelIndex, QAbstractItemModel, Signal, Qt
from PySide2 import QtWidgets
from nexus_constructor.model import GroupContainer, Group, Component, Dataset
import PySide2
import typing


class FieldListModel(QAbstractListModel):
    def __init__(self, parent: QWidget, group_container: GroupContainer):
        super().__init__(parent)
        self._group_container = group_container

    def rowCount(self, parent: PySide2.QtCore.QModelIndex) -> int:
        return sum(not isinstance(item, Group) for item in self._group_container.group.children)

    def data(self, index: PySide2.QtCore.QModelIndex, role=QModelIndex()) -> typing.Any:
        if not index.isValid():
            print("Return none")
            return None
        if index.row() >= self.rowCount(None) or index.row() < 0:
            print("Return none")
            return None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            used_string = f"Row {index.row()}"
            print(used_string)
            return QLabel(parent=self.parent(), text=used_string)
        print("Return none")

class FieldItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def commit(self, editor):
        pass

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QWidget:
        return QLineEdit(parent, text="Hi")

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        editor.setText("Hello")

    def setModelData(
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex
    ):
        # value = editor.text()
        # model.setData(index, value, Qt.EditRole)
        pass

    def updateEditorGeometry(
        self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ):
        editor.setGeometry(option.rect)

class FileListModel(QAbstractListModel):
    numberPopulated = Signal(int)

    def __init__(self, parent=None):
        super(FileListModel, self).__init__(parent)

        self.fileCount = 2
        self.fileList = ["File1", "File2"]

    def rowCount(self, parent=QModelIndex()):
        return self.fileCount

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() >= len(self.fileList) or index.row() < 0:
            return None

        if role == Qt.DisplayRole:
            return_val = QLabel(parent=self.parent())
            return_val.setText(self.fileList[index.row()])
            # return return_val
            return self.fileList[index.row()]

        # if role == Qt.BackgroundRole:
        #     batch = (index.row() // 100) % 2
        #     if batch == 0:
        #         return QtWidgets.qApp.palette().base()
        #
        #     return QtWidgets.qApp.palette().alternateBase()

        return None



class FieldList(QListView):
    def __init__(self, parent: QWidget, group_container: GroupContainer):
        super().__init__(parent)
        self._group_container = group_container
        # self._model = FieldListModel(parent, group_container)
        self._model = FileListModel(self)
        self._item_delegate = FieldItemDelegate(parent)
        self.setItemDelegate(self._item_delegate)
        self.setModel(self._model)

    def add_field(self):
        c_group = self._group_container.group
        new_dataset = Dataset(parent_node=c_group, name="test_name", values=123)
        c_group.children.append(new_dataset)

