from .dropdown_list import DropDownList
from PySide2.QtWidgets import QWidget
from nexus_constructor.model.writer_module_container import ModuleContainer
from nexus_constructor.ui_utils import validate_general_widget
from functools import partial
from nexus_constructor.model.module import StreamModules, StreamModule
from PySide2.QtCore import Signal
from PySide2.QtGui import QValidator
from typing import List


class StreamModuleValidator(QValidator):
    def __init__(self, module_container: ModuleContainer):
        super().__init__()
        self._module_container = module_container

    def validate(self, input: str, pos: int):
        if self._module_container.module.parent_node:
            list_of_streams = [
                s.writer_module
                for s in self._module_container.module.parent_node.children
                if isinstance(s, StreamModule) and s is not self._module_container.module
            ]
        if input == "" or input in list_of_streams:
            self.is_valid.emit(False)
            return QValidator.Intermediate
        self.is_valid.emit(True)
        return QValidator.Acceptable
    is_valid = Signal(bool)


class StreamTypeDropdownList(DropDownList):
    def __init__(self, parent: QWidget, module_container: ModuleContainer):
        super().__init__(parent)
        self._module_container = module_container
        self.addItems([m.value for m in StreamModules])
        self.setCurrentText(self._module_container.module.writer_module)
        self.setValidator(StreamModuleValidator(self._module_container))
        self.validator().is_valid.connect(partial(validate_general_widget, self))
        self.currentIndexChanged.connect(self._stream_type_change)

    def _stream_type_change(self, new_selection: int):
        pass

    def check_validity(self):
        self.validator().validate(self.currentText(), 0)
