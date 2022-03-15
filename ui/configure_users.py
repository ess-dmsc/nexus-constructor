import copy

from PySide2.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableView,
    QVBoxLayout,
)

from ui.base_table import BaseTableModel


class UserTableModel(BaseTableModel):
    @property
    def users(self):
        # Ignore users with no name set.
        return [copy.copy(user) for user in self._data if user["name"].strip() != ""]

    def are_users_unique(self):
        users = set()
        for user in self._data:
            name = user["name"].strip()
            if not name:
                continue
            if name in users:
                return False
            users.add(name)
        return True


class ConfigureUsersDialog(QDialog):
    def __init__(self, users):
        super().__init__()
        self.setWindowTitle("Configure Users")
        headings = ["name", "email", "facility_user_id", "affiliation"]
        self.model = UserTableModel(headings, users)

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

        self.error_text = QLabel()
        self.error_text.setStyleSheet("color: red;")
        self.layout.addWidget(self.error_text)

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
        if not self.model.are_users_unique():
            self.error_text.setText("Name must be unique for each user")
            return

        self.error_text.setText("")
        self.accept()

    def _complete_table(self):
        # The currently selected cell only updates the model when 'return' is
        # pressed or another cell is selected. If the user is updating a value
        # then clicks 'OK' without pressing 'return' then the change is lost.
        # This is a Qt thing - the workaround is to take focus from the table.
        self.button_box.button(self.button_box.Ok).setFocus()

    def _add_user_clicked(self):
        self.users_table.model().insertRow(self.model.num_rows)

    def _delete_user_clicked(self):
        rows_to_remove = set()
        for index in self.users_table.selectedIndexes():
            rows_to_remove.add(index.row())
        self.users_table.model().removeRows(list(rows_to_remove))

    def get_users(self):
        return self.model.users
