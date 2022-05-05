from functools import partial
from typing import List

from PySide2 import QtWidgets
from PySide2.QtCore import Signal
from PySide2.QtGui import QValidator

from nexus_constructor.model import Dataset
from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.unique_name import generate_unique_name


class FieldNameValidator(QValidator):
    def __init__(self, dataset: Dataset):
        super().__init__()
        self._dataset = dataset

    def validate(self, input: str, pos: int) -> QValidator.State:
        list_of_group_names: List[str] = []
        if self._dataset.parent_node:
            list_of_group_names = [
                g.name
                for g in self._dataset.parent_node.children
                if isinstance(g, Dataset) and g is not self._dataset
            ]
        if input == "" or input in list_of_group_names:
            self.is_valid.emit(False)
            return QValidator.Intermediate
        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)


class FieldNameEdit(QtWidgets.QLineEdit):
    def __init__(self, parent: QtWidgets.QWidget, dataset: Dataset):
        super().__init__(parent)
        self._dataset = dataset
        self.setText(self._dataset.name)
        self.setValidator(FieldNameValidator(dataset))
        self.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self,
                tooltip_on_accept="Dataset name is valid.",
                tooltip_on_reject="Dataset name is not valid. Suggestion: ",
                suggestion_callable=self.generate_name_suggestion,
            )
        )
        self.textEdited.connect(self._set_new_group_name)
        self.validator().validate(self.text(), 0)
        self.validator().is_valid.connect(self.is_valid.emit)

    def check_validity(self):
        self.validator().validate(self._dataset.name, 0)

    def _set_new_group_name(self, new_name: str):
        self._dataset.name = new_name

    def generate_name_suggestion(self):
        """
        Generates a component name suggestion for use in the tooltip when a component is invalid.
        :return: The component name suggestion, based on the current nx_class.
        """
        if not self._dataset.parent_node:
            return generate_unique_name(self.text().lstrip("NX"), [])
        return generate_unique_name(
            self.text().lstrip("NX"),
            [g for g in self._dataset.parent_node.children if isinstance(g, Dataset)],
        )

    is_valid = Signal(bool)
