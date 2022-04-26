from PySide2 import QtWidgets
from functools import partial
from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.unique_name import generate_unique_name
from PySide2.QtGui import QValidator
from PySide2.QtCore import Signal
from nexus_constructor.model.group import Group, GroupContainer


class GroupNameValidator(QValidator):
    def __init__(self, container: GroupContainer):
        super().__init__()
        self._container = container

    def validate(self, input: str, pos: int) -> QValidator.State:
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
        self.textEdited.connect(self._set_new_group_name)
        self.validator().validate(self.text(), 0)

    def _set_new_group_name(self, new_name: str):
        self._container.group.name = new_name

    def generate_name_suggestion(self):
        """
        Generates a component name suggestion for use in the tooltip when a component is invalid.
        :return: The component name suggestion, based on the current nx_class.
        """
        return generate_unique_name(
            self.text().lstrip("NX"),
            [
                g
                for g in self._container.group.parent_node.children
                if isinstance(g, Group)
            ],
        )
