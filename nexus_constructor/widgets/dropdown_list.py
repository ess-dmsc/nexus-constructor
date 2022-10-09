from typing import Optional

from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QComboBox, QWidget


class DropDownList(QComboBox):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._validator: Optional[QValidator] = None
        self.currentIndexChanged.connect(self._validate)

    def _validate(self, new_selection: int):
        if self._validator is not None:
            self._validator.validate(self.itemText(new_selection), new_selection)

    def setEditable(self, editable: bool) -> None:
        raise RuntimeError("DropDownList is not editable.")

    def setValidator(self, v: QValidator) -> None:
        self._validator = v

    def validator(self) -> QValidator:
        return self._validator
