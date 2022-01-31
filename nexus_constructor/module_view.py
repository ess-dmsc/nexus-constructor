from PySide2.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from nexus_constructor.field_utils import find_field_type
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.model.module import WriterModules


class ModuleView(QGroupBox):
    def __init__(self, module, parent: QWidget):
        super().__init__(module.writer_module.upper(), parent)
        layout = QVBoxLayout()
        self.field_widget = FieldWidget()
        layout.addWidget(self.field_widget)
        self.setLayout(layout)
        self.module = module
        self._set_existing_items()

    def _set_existing_items(self):
        module = self.module
        if self.module.writer_module == WriterModules.DATASET.value:
            update_function = find_field_type(module, [])
            if update_function is not None:
                update_function(module, self.field_widget)
        elif self.module.writer_module == WriterModules.LINK.value:
            pass
        else:
            update_function = find_field_type(module.parent_node, [])
            if update_function is not None:
                update_function(module.parent_node, self.field_widget)
