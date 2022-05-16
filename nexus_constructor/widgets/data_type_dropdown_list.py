from nexus_constructor.model.writer_module_container import ModuleContainer
from .dropdown_list import DropDownList
from PySide2.QtGui import QValidator
from PySide2.QtCore import Signal
from functools import partial
from nexus_constructor.ui_utils import validate_general_widget

TYPES = [
    "int8",
    "uint8",
    "int16",
    "uint16",
    "int32",
    "uint32",
    "int64",
    "uint64",
    "float",
    "double",
]


class DataTypeValidator(QValidator):
    def __init__(self, accept_string: bool = False):
        super().__init__()
        self.accept_string = accept_string

    def validate(self, input: str, pos: int):
        if input in TYPES or (input == "string" and self.accept_string):
            self.is_valid.emit(True)
            return QValidator.Acceptable
        self.is_valid.emit(False)
        return QValidator.Intermediate

    is_valid = Signal(bool)


class DataTypeDropDown(DropDownList):
    def __init__(self, parent, container: ModuleContainer, allow_string: bool = False):
        super().__init__(parent)
        self._container = container
        self.addItems(TYPES)
        if allow_string:
            self.addItems(
                [
                    "string",
                ]
            )
        self.setCurrentText(container.module.type)
        self.setValidator(DataTypeValidator(allow_string))
        self.validator().is_valid.connect(partial(validate_general_widget, self))
        self.currentIndexChanged.connect(self._set_data_type)
        self.check_validity()

    def _set_data_type(self):
        self._container.module.type = self.currentText()

    def check_validity(self):
        self.validator().validate(self.currentText(), 0)
