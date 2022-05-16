from functools import partial

from PySide2 import QtWidgets
from PySide2.QtCore import Signal

from nexus_constructor.model.writer_module_container import ModuleContainer
from nexus_constructor.ui_utils import line_edit_validation_result_handler
from nexus_constructor.validators import UnitValidator


class UnitLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent: QtWidgets.QWidget, container: ModuleContainer):
        super().__init__(parent)
        self._container = container
        self.setText(self._container.module.value_units)
        self.setValidator(UnitValidator())
        self.validator().is_valid.connect(
            partial(
                line_edit_validation_result_handler,
                self,
            )
        )
        self.textEdited.connect(self._set_unit)
        self.validator().validate(self.text(), 0)
        self.validator().is_valid.connect(self.is_valid.emit)

    def check_validity(self):
        self.validator().validate(self._container.module.value_units, 0)

    def _set_unit(self, new_unit: str):
        self._container.module.value_units = new_unit

    is_valid = Signal(bool)
