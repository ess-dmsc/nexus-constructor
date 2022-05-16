from typing import Optional
from nexus_constructor.model.writer_module_container import ModuleContainer
from PySide2.QtWidgets import QSpinBox


class PositiveIntegerSetting(QSpinBox):
    def __init__(self, parent, container: ModuleContainer, attribute_name: str):
        super().__init__(parent)
        self._container = container
        self._attribute_name = attribute_name
        self.setRange(0, 1_000_000)
        self.setValue(self._get_module_value())
        self.valueChanged.connect(self._set_module_value)

    def _get_module_value(self) -> Optional[int]:
        retrieved_value = getattr(self._container.module, self._attribute_name)
        if retrieved_value is None:
            return 0
        return retrieved_value

    def _set_module_value(self, new_value: int):
        if new_value == 0:
            new_value = None
        setattr(self._container.module, self._attribute_name, new_value)
