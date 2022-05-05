from functools import partial

from PySide2.QtWidgets import QWidget, QLineEdit, QComboBox
from PySide2.QtCore import Signal
from PySide2.QtGui import QValidator

from nexus_constructor.model import Dataset
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP
from nexus_constructor.ui_utils import line_edit_validation_result_handler
from .scalar_value_base import ScalarValueBase


class FieldValueValidator(QValidator):
    def __init__(
        self,
        dataset_type_combo: QComboBox,
    ):
        super().__init__()
        self._dataset_type_combo = dataset_type_combo

    def validate(self, input: str, pos: int) -> QValidator.State:
        if not input:  # More criteria here
            return self._emit_and_return(False)
        try:
            VALUE_TYPE_TO_NP[self._dataset_type_combo.currentText()](input)
        except ValueError:
            return self._emit_and_return(False)
        return self._emit_and_return(True)

    def _emit_and_return(self, valid: bool) -> QValidator.State:
        self.is_valid.emit(valid)
        return QValidator.Acceptable if valid else QValidator.Intermediate

    is_valid = Signal(bool)


class ScalarValueEdit(ScalarValueBase):
    def __init__(self, parent: QWidget, dataset: Dataset):
        super().__init__(parent, dataset)
        self._value_line_edit = QLineEdit(self)
        self._value_line_edit.setValidator(
            FieldValueValidator(
                self._value_type_combo,
            )
        )
        self._value_line_edit.validator().is_valid.connect(
            partial(self._validator.set_is_valid, self._value_line_edit)
        )
        self._value_line_edit.validator().is_valid.connect(
            partial(
                line_edit_validation_result_handler,
                self._value_line_edit,
                tooltip_on_accept="Value is cast-able to numpy type.",
                tooltip_on_reject="Value is not cast-able to selected numpy type.",
            )
        )

        self._value_line_edit.setPlaceholderText("value")
        self.layout().insertWidget(0, self._value_line_edit)
        self._value_line_edit.setText(str(self._dataset.values))

        self._value_line_edit.textEdited.connect(self._value_changed)
        self._dataset_type_changed()

    def _value_changed(self, new_value: str):
        try:
            self._dataset.values = VALUE_TYPE_TO_NP[
                self._value_type_combo.currentText()
            ](new_value)
        except ValueError:
            self._dataset.values = new_value

    def _dataset_type_changed(self):
        self._value_line_edit.validator().validate(self._value_line_edit.text(), 0)

    def check_validity(self):
        super().check_validity()
        self._dataset_type_changed()
