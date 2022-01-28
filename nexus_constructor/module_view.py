from PySide2.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from nexus_constructor.field_utils import find_field_type
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import WriterModules
from nexus_constructor.model.value_type import ValueTypes


class ModuleView(QGroupBox):
    def __init__(self, module, parent: QWidget, model: Model):
        super().__init__(module.writer_module.upper(), parent)
        layout = QVBoxLayout()
        self.field_widget = FieldWidget()
        layout.addWidget(self.field_widget)
        self.setLayout(layout)
        self.module = module
        self.model = model
        self._set_existing_items(module)

    def _set_existing_items(self, module):
        update_function = find_field_type(module, [])
        if update_function is not None:
            update_function(module, self.field_widget)
        self.field_widget.name = module.name
        if hasattr(module, "type") and not module.type:
            self.field_widget.dtype = ValueTypes.STRING

    def save_module_changes(self):
        if self.module.writer_module == WriterModules.DATASET.value:
            self.module.name = self.field_widget.name
            self.module.values = self.field_widget.value
            self.module.type = self.field_widget.dtype
        self.model.signals.module_changed.emit()
