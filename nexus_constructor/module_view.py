from PySide2.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from nexus_constructor.common_attrs import CommonAttrs, CommonKeys
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
        self._set_existing_items()

    def _set_existing_items(self):
        module = self.module
        update_function = find_field_type(module, [])
        if self.module.writer_module == WriterModules.DATASET.value:
            if update_function is not None:
                update_function(module, self.field_widget)
            self.field_widget.name = module.name
            if hasattr(module, CommonKeys.TYPE) and not module.type:
                self.field_widget.dtype = ValueTypes.STRING
            units = module.attributes.get_attribute_value(CommonAttrs.UNITS)
        elif self.module.writer_module == WriterModules.LINK.value:
            pass
        else:
            if update_function is not None:
                update_function(module.parent_node, self.field_widget)
            self.field_widget.name = module.parent_node.name
            units = module.parent_node.attributes.get_attribute_value(CommonAttrs.UNITS)
        if units:
            self.field_widget.units = units

    def save_module_changes(self):
        if self.module.writer_module == WriterModules.DATASET.value:
            self.module.name = self.field_widget.name
            self.module.values = self.field_widget.value
            self.module.type = self.field_widget.dtype
            self.module.attributes.set_attribute_value(
                CommonAttrs.UNITS, self.field_widget.units
            )
        elif self.module.writer_module == WriterModules.LINK.value:
            pass
        else:
            self.module.parent_node.name = self.field_widget.name
            self.module.type = self.field_widget.dtype
            self.module.parent_node.attributes.set_attribute_value(
                CommonAttrs.UNITS, self.field_widget.units
            )
            self.module.parent_node.attributes.type = self.field_widget.dtype
        self.model.signals.module_changed.emit()
