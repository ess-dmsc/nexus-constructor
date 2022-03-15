import copy
from typing import Dict, List

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt


class SampleTableModel(QAbstractTableModel):
    def __init__(self, data: List[Dict[str, str]]):
        super().__init__()
        self._headings = ["name", "formula", "number of", "mass/volume", "density"]
        self._data: List[Dict[str, str]] = copy.deepcopy(data)

    def data(self, index, role=None):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._data[index.row()][self._headings[index.column()]]

    def setData(self, index, value, role=None):
        if role != Qt.EditRole:
            return False

        row, column_key = index.row(), self._headings[index.column()]
        self._data[row][column_key] = value
        return True

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self._headings)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._data)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headings[section]

    def add_new_row(self, position):
        self._data.insert(position, {k: "" for k in self._headings})

    def insertRow(self, position, index=QModelIndex()):
        self.beginInsertRows(index, position, position)
        self.add_new_row(position)
        self.endInsertRows()
        return True

    def removeRows(self, rows, index=QModelIndex()):
        for row in sorted(rows, reverse=True):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._data[row]
            self.endRemoveRows()
        return True

    @property
    def num_rows(self):
        return len(self._data)
