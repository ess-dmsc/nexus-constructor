import copy
from typing import Dict, List

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide2.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableView,
    QVBoxLayout,
)


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


class ConfigureSamplesDialog(QDialog):
    def __init__(self, samples):
        super().__init__()
        self.setWindowTitle("Configure Users")
        self.model = SampleTableModel(samples)

        self.layout = QVBoxLayout()
        self.table_layout = QHBoxLayout()
        self.sample_table = QTableView()
        self.sample_table.setModel(self.model)
        self.sample_table.horizontalHeader().setStretchLastSection(True)
        self.table_layout.addWidget(self.sample_table)

        self.table_buttons_layout = QVBoxLayout()
        self.add_sample_button = QPushButton()
        self.add_sample_button.setText("Add Sample")
        self.add_sample_button.clicked.connect(self._add_sample_clicked)
        self.delete_sample_button = QPushButton()
        self.delete_sample_button.setText("Delete Sample")
        self.delete_sample_button.clicked.connect(self._delete_sample_clicked)
        self.table_buttons_layout.addSpacerItem(
            QSpacerItem(0, 0, vData=QSizePolicy.Expanding)
        )
        self.table_buttons_layout.addWidget(self.add_sample_button)
        self.table_buttons_layout.addWidget(self.delete_sample_button)
        self.table_buttons_layout.addSpacerItem(
            QSpacerItem(0, 0, vData=QSizePolicy.Expanding)
        )
        self.table_layout.addLayout(self.table_buttons_layout)

        self.layout.addLayout(self.table_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self._on_accepted_clicked)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

        self.resize(600, 400)

    def _on_accepted_clicked(self):
        self._complete_table()
        self.accept()

    def _complete_table(self):
        self.button_box.button(self.button_box.Ok).setFocus()

    def _add_user_clicked(self):
        self.sample_table.model().insertRow(self.model.num_rows)

    def _delete_user_clicked(self):
        rows_to_remove = set()
        for index in self.sample_table.selectedIndexes():
            rows_to_remove.add(index.row())
        self.sample_table.model().removeRows(list(rows_to_remove))
