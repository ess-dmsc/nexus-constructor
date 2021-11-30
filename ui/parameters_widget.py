from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)

from nexus_constructor.model.model import Model
from ui.configure_users import ConfigureUsersDialog


class ParametersView(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.model = None
        self.setLayout(QVBoxLayout())
        self.setParent(parent)

        self.proposal_layout = QHBoxLayout()
        self.proposal_label = QLabel()
        self.proposal_label.setText("Proposal ID:")
        self.proposal_text = QLineEdit()
        self.proposal_text.textEdited.connect(self._proposal_text_changed)
        self.proposal_placeholder = QCheckBox()
        self.proposal_placeholder.toggled.connect(self._proposal_id_checked_changed)
        self.proposal_placeholder.setText("Use placeholder")
        self.proposal_layout.addWidget(self.proposal_label)
        self.proposal_layout.addWidget(self.proposal_text)
        self.proposal_layout.addWidget(self.proposal_placeholder)
        self.layout().addLayout(self.proposal_layout)

        self.title_layout = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setText("Title:")
        self.title_text = QLineEdit()
        self.title_text.textEdited.connect(self._title_text_changed)
        self.title_placeholder = QCheckBox()
        self.title_placeholder.toggled.connect(self._title_checked_changed)
        self.title_placeholder.setText("Use placeholder")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addWidget(self.title_text)
        self.title_layout.addWidget(self.title_placeholder)
        self.layout().addLayout(self.title_layout)

        self.users_layout = QHBoxLayout()
        self.edit_users_button = QPushButton()
        self.edit_users_button.setText("Configure users")
        self.edit_users_button.clicked.connect(self._edit_users)
        self.users_placeholder = QCheckBox()
        self.users_placeholder.toggled.connect(self._users_checked_changed)
        self.users_placeholder.setText("Use placeholder")
        self.users_layout.addSpacerItem(QSpacerItem(0, 0, hData=QSizePolicy.Expanding))
        self.users_layout.addWidget(self.edit_users_button)
        self.users_layout.addWidget(self.users_placeholder)
        self.layout().addLayout(self.users_layout)

    def set_up_model(self, model: Model):
        self.model = model
        proposal_id, is_placeholder = model.entry.proposal_id
        if is_placeholder:
            self.proposal_placeholder.setChecked(True)
            self.proposal_text.setText("")
        else:
            self.proposal_placeholder.setChecked(False)
            self.proposal_text.setText(proposal_id)

        title, is_placeholder = model.entry.title
        if is_placeholder:
            self.title_placeholder.setChecked(True)
            self.title_text.setText("")
        else:
            self.title_placeholder.setChecked(False)
            self.title_text.setText(title)

        if model.entry.users_placeholder:
            self.users_placeholder.setChecked(True)
        else:
            self.users_placeholder.setChecked(False)

    def _proposal_id_checked_changed(self):
        if self.proposal_placeholder.isChecked():
            self.model.entry.proposal_id = ("", True)
        else:
            self.model.entry.proposal_id = (self.proposal_text.text(), False)
        self.proposal_text.setEnabled(not self.proposal_placeholder.isChecked())

    def _proposal_text_changed(self, text):
        self.model.entry.proposal_id = (text, self.proposal_placeholder.isChecked())

    def _title_checked_changed(self):
        if self.title_placeholder.isChecked():
            self.model.entry.title = ("", True)
        else:
            self.model.entry.title = (self.title_text.text(), False)
        self.title_text.setEnabled(not self.title_placeholder.isChecked())

    def _title_text_changed(self, text):
        self.model.entry.title = (text, self.title_placeholder.isChecked())

    def _edit_users(self):
        dialog = ConfigureUsersDialog(self.model.entry.users)
        if dialog.exec_():
            self.model.entry.users = dialog.get_users()

    def _users_checked_changed(self):
        if self.users_placeholder.isChecked():
            self.model.entry.users_placeholder = True
        else:
            self.model.entry.users_placeholder = False
        self.edit_users_button.setEnabled(not self.users_placeholder.isChecked())
