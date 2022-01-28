from PySide2.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from nexus_constructor.field_utils import find_field_type
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.model.value_type import ValueTypes


class ModuleView(QGroupBox):
    def __init__(self, module, parent: QWidget):
        super().__init__(module.writer_module.upper(), parent)
        layout = QVBoxLayout()
        self.field_widget = FieldWidget()
        layout.addWidget(self.field_widget)
        self.setLayout(layout)
        self._set_existing_items(module)

    def _set_existing_items(self, module):
        update_function = find_field_type(module, [])
        if update_function is not None:
            update_function(module, self.field_widget)
        self.field_widget.name = module.name
        if hasattr(module, "type") and not module.type:
            self.field_widget.dtype = ValueTypes.STRING
