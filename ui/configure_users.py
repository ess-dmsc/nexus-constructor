import copy
from typing import Dict, List

from PySide2.QtCore import QAbstractTableModel, Qt
from PySide2.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QDialogButtonBox,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)


class TableModel(QAbstractTableModel):
    def __init__(self, data: List[Dict[str, str]]):
        super().__init__()
        self._headings = ["name", "email", "facility_user_id", "affiliation"]
        self._data: List[Dict[str, str]] = copy.deepcopy(data)

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._data[index.row()][self._headings[index.column()]]

    def setData(self, index, value, role):
        if role != Qt.EditRole:
            return False

        row, column_key = index.row(), self._headings[index.column()]
        self._data[row][column_key] = value
        return True

    def columnCount(self, index):
        return len(self._headings)

    def rowCount(self, index):
        return len(self._data)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headings[section]

    def add_new_user(self):
        self._data.append({k: "" for k in self._headings})
        self.layoutChanged.emit()

    def delete_users(self, indexes):
        for row in sorted(indexes, reverse=True):
            self._data.pop(row)
        self.layoutChanged.emit()

    @property
    def users(self):
        # Ignore users with no name set.
        return [copy.copy(user) for user in self._data if user["name"].strip() != ""]


class ConfigureUsersDialog(QDialog):
    def __init__(self, users):
        super().__init__()
        self.setWindowTitle("Configure Users")
        self.model = TableModel(users)

        self.layout = QVBoxLayout()
        self.table_layout = QHBoxLayout()
        self.users_table = QTableView()
        self.users_table.setModel(self.model)
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.table_layout.addWidget(self.users_table)

        self.table_buttons_layout = QVBoxLayout()
        self.add_user_button = QPushButton()
        self.add_user_button.setText("Add User")
        self.add_user_button.clicked.connect(self._add_user_clicked)
        self.delete_user_button = QPushButton()
        self.delete_user_button.setText("Delete User")
        self.delete_user_button.clicked.connect(self._delete_user_clicked)
        self.table_buttons_layout.addSpacerItem(
            QSpacerItem(0, 0, vData=QSizePolicy.Expanding)
        )
        self.table_buttons_layout.addWidget(self.add_user_button)
        self.table_buttons_layout.addWidget(self.delete_user_button)
        self.table_buttons_layout.addSpacerItem(
            QSpacerItem(0, 0, vData=QSizePolicy.Expanding)
        )
        self.table_layout.addLayout(self.table_buttons_layout)

        self.layout.addLayout(self.table_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

        self.resize(600, 400)

    def _add_user_clicked(self):
        self.model.add_new_user()

    def _delete_user_clicked(self):
        indexes = [index.row() for index in self.users_table.selectedIndexes()]
        self.model.delete_users(indexes)

    def get_users(self):
        return self.model.users
