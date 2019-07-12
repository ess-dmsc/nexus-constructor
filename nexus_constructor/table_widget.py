import numpy as np
import typing
from PySide2.QtCore import QModelIndex, QAbstractTableModel, Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QTableView, QToolBar, QAction


class TableWidget(QWidget):
    def __init__(self, type: np.dtype = np.byte, parent=None):
        super().__init__(parent)
        self.model = TableModel(type=type, parent=self)
        self.setLayout(QGridLayout())

        self.toolbox = QToolBar()

        self.add_row_button = QAction(text="➕ Add Row")
        self.add_row_button.triggered.connect(self.model.add_row)
        self.remove_row_button = QAction(text="➖ Remove Row")
        self.add_column_button = QAction(text="➕ Add Column")
        self.add_column_button.triggered.connect(self.model.add_column)
        self.remove_column_button = QAction(text="➖ Remove Column")

        buttons = [
            self.add_row_button,
            self.remove_row_button,
            self.add_column_button,
            self.remove_column_button,
        ]

        [self.toolbox.addAction(button) for button in buttons]

        self.layout().addWidget(self.toolbox)
        self.view = QTableView()
        self.layout().addWidget(self.view)


class TableModel(QAbstractTableModel):
    def __init__(self, type: np.dtype = np.byte, parent=None):
        super().__init__()
        self.array = np.array([], dtype=type)

    def add_row(self):
        self.beginInsertRows(QModelIndex(), 0, 1)
        np.append(self.array, [1, 2, 3])
        self.endInsertRows()

    def add_column(self):
        pass

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return self.array.shape[0]

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return self.array.shape[1]

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            return self.array[index.row(), index.column()]
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> typing.Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.array.columns[section]
            elif orientation == Qt.Vertical:
                return orientation
        return None
