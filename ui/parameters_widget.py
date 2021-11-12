from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
)

from nexus_constructor.model.model import Model


class ParametersView(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.model = None
        self.setLayout(QVBoxLayout())
        self.setParent(parent)

        self.proposal_layout = QHBoxLayout()
        self.proposal_label = QLabel()
        self.proposal_label.setText("Proposal ID:")
        self.prop_text = QLineEdit()
        self.prop_text.textEdited.connect(self._prop_text_changed)
        self.prop_placeholder = QCheckBox()
        self.prop_placeholder.toggled.connect(self._prop_id_checked_changed)
        self.prop_placeholder.setText("Use placeholder")

        self.proposal_layout.addWidget(self.proposal_label)
        self.proposal_layout.addWidget(self.prop_text)
        self.proposal_layout.addWidget(self.prop_placeholder)
        self.layout().addLayout(self.proposal_layout)

    def set_up_model(self, model: Model):
        self.model = model
        proposal_id, is_placeholder = model.entry.proposal_id
        if is_placeholder:
            self.prop_placeholder.setChecked(True)
            self.prop_text.setText("")
        else:
            self.prop_placeholder.setChecked(False)
            self.prop_text.setText(proposal_id)

    def _prop_id_checked_changed(self):
        if self.prop_placeholder.isChecked():
            self.model.entry.proposal_id = ("", True)
        else:
            self.model.entry.proposal_id = (self.prop_text.text(), False)
        self.prop_text.setEnabled(not self.prop_placeholder.isChecked())

    def _prop_text_changed(self, text):
        self.model.entry.proposal_id = (text, self.prop_placeholder.isChecked())
