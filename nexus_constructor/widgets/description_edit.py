from PySide6 import QtWidgets

from nexus_constructor.model import GroupContainer


class DescriptionEdit(QtWidgets.QLineEdit):
    def __init__(self, parent: QtWidgets.QWidget, container: GroupContainer):
        super().__init__(parent)
        self._container = container
        self.textEdited.connect(self._set_new_description)
        self.setText(self._container.group.description)

    def _set_new_description(self, new_description: str):
        self._container.group.description = new_description
