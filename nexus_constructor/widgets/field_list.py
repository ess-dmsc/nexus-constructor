from PySide2.QtWidgets import QListView, QWidget, QLabel
from PySide2.QtCore import QAbstractListModel, QModelIndex
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
            return None
        if index.row() >= self.rowCount(None) or index.row() < 0:
            return None
        print("Return data.")
        return QLabel(f"Row {index.row()}")


class FieldList(QWidget):
    def __init__(self, parent: QWidget, group_container: GroupContainer):
        super().__init__(parent)
        self._group_container = group_container
        self._model = FieldListModel(parent, group_container)
        self.view = QListView()
        self.view.setModel(self._model)

    def add_field(self):
        c_group = self._group_container.group
        new_dataset = Dataset(parent_node=c_group, name="test_name", values=123)
        c_group.children.append(new_dataset)

