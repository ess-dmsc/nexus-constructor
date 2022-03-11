from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.field_utils import find_field_type
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import StreamModules, WriterModules


class ModuleView(QGroupBox):
    def __init__(self, module, parent: QWidget, model: Model):
        super().__init__(module.writer_module.upper(), parent)
        self.setFixedHeight(65)
        self.model = model
        self._setup_frame(module)

    def _setup_frame(self, module):
        self.layout = QHBoxLayout()
        if module.writer_module in [StreamMode.value for StreamMode in StreamModules]:
            topic = module.topic if module.topic else "not specified"
            source = module.source if module.topic else "not specified"
            self.layout.addWidget(self._get_label(f"topic: {topic}, "))
            self.layout.addWidget(self._get_label(f"source: {source}"))
        elif module.writer_module == WriterModules.LINK.value:
            name = module.name if module.name else "not specified"
            source = module.source if module.source else "not specified"
            self.layout.addWidget(self._get_label(f"name: {name}, "))
            self.layout.addWidget(self._get_label(f"source: {source}"))
        elif module.writer_module == WriterModules.DATASET.value:
            name = module.name if module.name else "not specified"
            dtype = module.type if module.type else "not specified"
            self.layout.addWidget(self._get_label(f"name: {name}, "))
            self.layout.addWidget(self._get_label(f"data type: {dtype}"))
        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)

    @staticmethod
    def _get_label(content):
        label = QLabel(content)
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        return label


class ModuleViewEditable(QGroupBox):
    def __init__(self, module, parent: QWidget, model: Model):
        super().__init__(module.writer_module.upper(), parent)
        layout = QVBoxLayout()
        self.field_widget = FieldWidget(module.parent_node)
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
            or self.module.writer_module
            in [StreamMode.value for StreamMode in StreamModules]
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
            self.module.values = self.field_widget.value.values  # type: ignore
            self.module.type = self.field_widget.dtype
            self.module.attributes.set_attribute_value(
                CommonAttrs.UNITS, self.field_widget.units
            )
        elif self.module.writer_module in [
            StreamMode.value for StreamMode in StreamModules
        ]:
            self.module.source = self.field_widget.value.source  # type: ignore
            self.module.topic = self.field_widget.value.topic  # type: ignore
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
