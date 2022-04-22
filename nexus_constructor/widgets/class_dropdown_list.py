from PySide2 import QtWidgets
from PySide2.QtGui import QValidator, QBrush
from nexus_constructor.component_type import NX_CLASSES, COMPONENT_TYPES, ENTRY_CLASS_NAME
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.widgets.dropdown_list import DropDownList
from PySide2.QtCore import Signal
from nexus_constructor.model.group import GroupContainer, Group
from PySide2.QtCore import Qt
from nexus_constructor.ui_utils import validate_general_widget
from functools import partial


class NXClassValidator(QValidator):
    def __init__(self):
        super().__init__()

    def validate(self, input: str, pos: int):
        if not input or input not in NX_CLASSES:
            self.is_valid.emit(False)
            return QValidator.Intermediate
        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)


class ClassDropDownList(DropDownList):
    def __init__(self, parent: QtWidgets.QWidget, container: GroupContainer):
        super().__init__(parent)
        self._container = container
        self.setValidator(NXClassValidator())
        self.validator().is_valid.connect(
            partial(validate_general_widget,
                    self)
        )

        sorted_groups_list = list(NX_CLASSES - COMPONENT_TYPES)
        sorted_groups_list.sort()
        sorted_component_list = list(COMPONENT_TYPES)
        sorted_component_list.sort()
        if isinstance(self._container.group, Component):
            self.addItem("- Components", userData=None)
            self.model().item(0).setEnabled(False)
            self.addItems(sorted_component_list)
            self.setCurrentIndex(sorted_component_list.index(self._container.group.nx_class) + 1)
        elif isinstance(self._container.group, Entry):
            self.addItems([ENTRY_CLASS_NAME])
        elif isinstance(self._container.group, Group) and self._container.group.nx_class:
            self.addItem("- Groups", userData=None)
            self.model().item(0).setEnabled(False)
            self.addItems(sorted_groups_list)
            self.setCurrentIndex(sorted_groups_list.index(self._container.group.nx_class) + 1)
        else:
            self.addItem("(None)", userData=None)
            self.model().item(0).setBackground(QBrush(Qt.red))
            self.addItem("- Components", userData=None)
            self.model().item(1).setEnabled(False)
            self.addItems(sorted_component_list)
            self.addItem("- Groups", userData=None)
            self.model().item(
                self.count() - 1
            ).setEnabled(False)
            self.addItems(sorted_groups_list)
        self.currentIndexChanged.connect(self._set_nx_class)

    def _set_nx_class(self):
        self._container.group.nx_class = self.currentText()

