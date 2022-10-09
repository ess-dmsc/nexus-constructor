from functools import partial
from typing import List

from PySide6 import QtWidgets
from PySide6.QtCore import QStringListModel, Qt, Signal
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QCompleter

from nexus_constructor.model import Group, GroupContainer
from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.unique_name import generate_unique_name


class GroupNameValidator(QValidator):
    def __init__(self, container: GroupContainer):
        super().__init__()
        self._container = container

    def validate(self, input: str, pos: int) -> QValidator.State:
        list_of_group_names: List[str] = []
        if self._container.group.parent_node:
            list_of_group_names = [
                g.name
                for g in self._container.group.parent_node.children
                if isinstance(g, Group) and g is not self._container.group
            ]
        if input == "" or input in list_of_group_names:
            self.is_valid.emit(False)
            return QValidator.Intermediate
        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)


class GroupNameEdit(QtWidgets.QLineEdit):
    def __init__(self, parent: QtWidgets.QWidget, container: GroupContainer):
        super().__init__(parent)
        self._container = container
        self.setValidator(GroupNameValidator(container))
        self.setText(self._container.group.name)
        self.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self,
                tooltip_on_accept="Group name is valid.",
                tooltip_on_reject="Group name is not valid. Suggestion: ",
                suggestion_callable=self.generate_name_suggestion,
            )
        )
        self.validator().validate(self.text(), 0)
        self.setCompleter(QCompleter())

    def set_new_group_name(self):
        self._container.group.name = self.text()

    def generate_name_suggestion(self):
        """
        Generates a component name suggestion for use in the tooltip when a component is invalid.
        :return: The component name suggestion, based on the current nx_class.
        """
        if not self._container.group.parent_node:
            return generate_unique_name(self.text().lstrip("NX"), [])
        return generate_unique_name(
            self.text().lstrip("NX"),
            [
                g
                for g in self._container.group.parent_node.children
                if isinstance(g, Group)
            ],
        )

    def focusInEvent(self, event):
        self.completer().complete()
        super(GroupNameEdit, self).focusInEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            self.completer().complete()
        else:
            super().keyPressEvent(event)

    def update_possible_fields(self, possible_fields: List[str]):
        model = QStringListModel()
        model.setStringList(sorted(possible_fields))
        self.completer().setModel(model)
