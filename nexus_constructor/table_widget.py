from functools import partial

import numpy as np
import typing
from PySide2.QtCore import QModelIndex, QAbstractTableModel, Qt, Signal
from PySide2.QtWidgets import (
    QWidget,
    QGridLayout,
    QTableView,
    QToolBar,
    QAction,
    QAbstractItemView,
)


class TableWidget(QWidget):
    def __init__(self, type: np.dtype = np.byte, parent=None):
        super().__init__(parent)
        self.model = TableModel(dtype=type, parent=self)
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.model.dataChanged.connect(self.view.update)

        self.setLayout(QGridLayout())
        self.toolbox = QToolBar()
        self.add_row_button = QAction(text="➕ Add Row")
        self.add_row_button.triggered.connect(self.model.add_row)
        self.remove_row_button = QAction(text="➖ Remove Row")
        self.remove_row_button.triggered.connect(self.model.delete_row)
        self.add_column_button = QAction(text="➕ Add Column")
        self.add_column_button.triggered.connect(self.model.add_column)
        self.remove_column_button = QAction(text="➖ Remove Column")
        self.remove_column_button.triggered.connect(self.model.delete_column)

        self.toolbox.addAction(self.add_row_button)
        self.toolbox.addAction(self.remove_row_button)
        self.toolbox.addAction(self.add_column_button)
        self.toolbox.addAction(self.remove_column_button)

        self.layout().addWidget(self.toolbox)
        self.layout().addWidget(self.view)


class TableModel(QAbstractTableModel):

    dataChanged = Signal(QModelIndex, QModelIndex)

    def __init__(self, dtype: np.dtype, parent=None):
        super().__init__()
        self.setParent(parent)
        self.array = np.array([[0]], dtype=dtype)

    def update_array_dtype(self, dtype: np.dtype):
        """
        Updates the array dataset type. If there is existing data in the array, it tries to cast the values to the new dtype. If not or if numpy is unable to cast the values, a new array is created.
        :param dtype: The new dataset type to set the array to.
        """
        self.beginResetModel()
        try:
            self.array = np.array(self.array.data, dtype=dtype)
        except ValueError:
            self.array = np.array([[0]], dtype=dtype)
        self.endResetModel()

    def add_row(self):
        self.beginInsertRows(QModelIndex(), self.array.size, self.array.shape[0])
        self.array = np.concatenate(
            (self.array, np.array([[0]], dtype=self.array.dtype))
        )
        self.endInsertRows()

    def add_column(self):
        pass

    def delete_row(self):
        for index in self.parent().view.selectedIndexes():
            self.array = np.delete(self.array, index.row())

    def delete_column(self):
        pass

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """
        Dictates how many rows there are in the table.
        :param parent: Unused.
        :return: Number of elements in each dimension.
        """
        return self.array.shape[0]

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """
        Dictates how many columns there are in the table.
        :param parent: Unused.
        :return: Number of dimensions there are in the array.
        """
        return self.array.shape[1]

    def data(self, index: QModelIndex, role: int = ...) -> str:
        if role == Qt.DisplayRole or role == Qt.EditRole:
            value = self.array[index.row()][index.column()]
            print(value)
            return str(value)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return (
            super(TableModel, self).flags(index)
            | Qt.ItemIsEditable
            | Qt.ItemIsEnabled
            | Qt.ItemIsSelectable
        )

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> typing.Any:
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if orientation == Qt.Vertical:
                return f"{section:d}"
            if orientation == Qt.Horizontal:
                return f"{section:d}"
        return None

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if index.isValid() and role == Qt.EditRole and value:
            # self.beginResetModel()
            self.array[index.row()][index.column()] = value
            print(self.array)
            self.dataChanged.emit(index, index)
            # self.endResetModel()
            return True
        return False
