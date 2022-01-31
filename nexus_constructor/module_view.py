from PySide2.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.field_utils import find_field_type
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import WriterModules


class ModuleView(QGroupBox):
    def __init__(self, module, parent: QWidget, model: Model):
        super().__init__(module.writer_module.upper(), parent)
        layout = QVBoxLayout()
        self.field_widget = FieldWidget()
        layout.addWidget(self.field_widget)
        self.setLayout(layout)
        self.module = module
        self.model = model
        self._set_existing_items()

    def _set_existing_items(self):
        module = self.module
        if (
            self.module.writer_module == WriterModules.DATASET.value
            or self.module.writer_module == WriterModules.LINK.value
        ):
            update_function = find_field_type(module, [])
            if update_function is not None:
                update_function(module, self.field_widget)
        else:
            update_function = find_field_type(module.parent_node, [])
            if update_function is not None:
                update_function(module.parent_node, self.field_widget)

    def save_module_changes(self):
        if self.module.writer_module == WriterModules.DATASET.value:
            self.module.name = self.field_widget.name
            self.module.values = self.field_widget.value.values
            self.module.type = self.field_widget.dtype
            self.module.attributes.set_attribute_value(
                CommonAttrs.UNITS, self.field_widget.units
            )
        elif self.module.writer_module == WriterModules.LINK.value:
            self.module.source = self.field_widget.value.source  # type: ignore
            self.module.name = self.field_widget.name
        else:
            self.module.parent_node.name = self.field_widget.name
            self.module.type = self.field_widget.dtype
            self.module.parent_node.attributes.set_attribute_value(
                CommonAttrs.UNITS, self.field_widget.units
            )

        self.model.signals.module_changed.emit()
