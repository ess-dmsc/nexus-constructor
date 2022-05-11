from functools import partial

from PySide2.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QFrame, QLabel
from PySide2.QtCore import Signal

from nexus_constructor.model.writer_module_container import ModuleContainer
from nexus_constructor.ui_utils import line_edit_validation_result_handler
from nexus_constructor.validators import NoEmptyStringValidator, MultiItemValidator


class LinkEdit(QWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent)
        self._module_container = container
        self.setLayout(QHBoxLayout())

        self._link_name_edit = QLineEdit(self)
        self._link_name_edit.setPlaceholderText("Link name")
        self._link_name_edit.setValidator(NoEmptyStringValidator())
        self._link_target_edit = QLineEdit(self)
        self._link_target_edit.setPlaceholderText("Link target")
        self._link_target_edit.setValidator(NoEmptyStringValidator())

        self._add_line()
        self.layout().addWidget(QLabel("Name:"))
        self.layout().addWidget(self._link_name_edit)
        self._add_line()
        self.layout().addWidget(QLabel("Target:"))
        self.layout().addWidget(self._link_target_edit)

        self._module_validator = MultiItemValidator()

        self._link_name_edit.validator().is_valid.connect(
            partial(self._module_validator.set_is_valid, self._link_name_edit)
        )
        self._link_target_edit.validator().is_valid.connect(
            partial(self._module_validator.set_is_valid, self._link_target_edit)
        )

        self._link_name_edit.validator().is_valid.connect(
            partial(
                line_edit_validation_result_handler,
                self._link_name_edit,
            )
        )

        self._link_target_edit.validator().is_valid.connect(
            partial(
                line_edit_validation_result_handler,
                self._link_target_edit,
            )
        )

        self._link_name_edit.setText(self._module_container.module.name)
        self._link_target_edit.setText(self._module_container.module.target)
        self._link_name_edit.textEdited.connect(self._link_name_edited)
        self._link_target_edit.textEdited.connect(self._target_edited)

    def _add_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(line)

    def _link_name_edited(self, new_link_name: str):
        self._module_container.module.name = new_link_name

    def _target_edited(self, new_target: str):
        self._module_container.module.target = new_target

    def check_validity(self):
        self._link_name_edit.validator().validate(self._link_name_edit.text(), 0)
        self._link_target_edit.validator().validate(self._link_target_edit.text(), 0)

    is_valid = Signal(bool)
