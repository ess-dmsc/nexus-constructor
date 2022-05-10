from functools import partial

from PySide2.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QComboBox, QPushButton
from PySide2.QtCore import Signal, Qt

from nexus_constructor.model.module import StreamModule, StreamModules, WriterModules, WriterModuleClasses
from nexus_constructor.model.writer_module_container import ModuleContainer
from nexus_constructor.ui_utils import line_edit_validation_result_handler
from nexus_constructor.validators import NoEmptyStringValidator, MultiItemValidator


class FileWriterModuleEdit(QWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent)
        self._module_container = container
        self.setLayout(QHBoxLayout())
        self._module_type_combo: QComboBox = QComboBox(self)
        self._module_type_combo.addItems([m.value for m in StreamModules])
        self._module_type_combo.setCurrentText(container.module.writer_module)

        self._topic_edit = QLineEdit(self)
        self._topic_edit.setPlaceholderText("Topic")
        self._topic_edit.setValidator(NoEmptyStringValidator())
        self._source_edit = QLineEdit(self)
        self._source_edit.setPlaceholderText("Source name")
        self._source_edit.setValidator(NoEmptyStringValidator())
        self._more_options = QPushButton("More")

        self.layout().addWidget(self._module_type_combo)
        self.layout().addWidget(self._topic_edit)
        self.layout().addWidget(self._source_edit)
        self.layout().addWidget(self._more_options)

        self._module_validator = MultiItemValidator()

        self._topic_edit.validator().is_valid.connect(
            partial(self._module_validator.set_is_valid, self._topic_edit)
        )
        self._source_edit.validator().is_valid.connect(
            partial(self._module_validator.set_is_valid, self._source_edit)
        )

        self._topic_edit.validator().is_valid.connect(
            partial(
                line_edit_validation_result_handler,
                self._topic_edit,
            )
        )

        self._source_edit.validator().is_valid.connect(
            partial(
                line_edit_validation_result_handler,
                self._source_edit,
            )
        )

        self._topic_edit.setText(self._module_container.module.topic)
        self._source_edit.setText(self._module_container.module.source)
        self._topic_edit.textEdited.connect(self._topic_edited)
        self._source_edit.textEdited.connect(self._source_edited)

        self._module_type_combo.currentIndexChanged.connect(self._handle_module_change)

    #     self._units_line_edit.setPlaceholderText("unit")
    #     self._units_line_edit.setMaximumWidth(20)
    #     self._units_line_edit.setMaximumWidth(50)
    #
    #     self.layout().addWidget(self._value_type_combo)
    #     self.layout().addWidget(self._units_line_edit)
    #
    #     self.layout().setAlignment(Qt.AlignLeft)
    #
    #     self._value_type_combo.currentIndexChanged.connect(self._dataset_type_changed)
    #     self._units_line_edit.textEdited.connect(self._unit_changed)
    #
    #     if self._dataset.attributes.contains_attribute(CommonAttrs.UNITS):
    #         self._units_line_edit.setText(
    #             self._dataset.attributes.get_attribute_value(CommonAttrs.UNITS)
    #         )
    #     self._value_type_combo.setCurrentText(
    #         ValueTypes.STRING if not self._dataset.type else self._dataset.type
    #     )
    #     self._units_line_edit.setText(
    #         self._dataset.attributes.get_attribute_value(CommonAttrs.UNITS)
    #     )
    #
    # def _unit_changed(self, new_unit: str):
    #     if not new_unit:
    #         if self._dataset.attributes.contains_attribute(CommonAttrs.UNITS):
    #             self._dataset.attributes.remove_attribute(CommonAttrs.UNITS)
    #         return
    #     self._dataset.attributes.set_attribute_value(CommonAttrs.UNITS, new_unit)

    def _handle_module_change(self, new_index: int):
        module_map = {WriterModules.F142.value: WriterModuleClasses.F142,
                      WriterModules.EV42.value: WriterModuleClasses.EV42,
                      WriterModules.TDCTIME.value: WriterModuleClasses.TDCTIME,
                      WriterModules.NS10.value: WriterModuleClasses.NS10,
                      WriterModules.SENV.value: WriterModuleClasses.SENV,
                      WriterModules.HS00.value: WriterModuleClasses.HS00,
                      WriterModules.ADAR.value: WriterModuleClasses.ADAR,
                      }
        c_module_type = self._module_container.module.writer_module
        new_module_type = self._module_type_combo.itemText(new_index)
        if c_module_type != new_module_type:
            new_module = module_map[new_module_type].value(parent_node=self._module_container.module.parent_node, topic=self._module_container.module.topic, source=self._module_container.module.source)
            module_index = self._module_container.module.parent_node.children.index(self._module_container.module)
            self._module_container.module.parent_node.children[module_index] = new_module
            self._module_container.module = new_module

    def _source_edited(self, new_source: str):
        self._module_container.module.source = new_source

    def _topic_edited(self, new_topic: str):
        self._module_container.module.topic = new_topic

    def check_validity(self):
        self._topic_edit.validator().validate(self._topic_edit.text(), 0)
        self._source_edit.validator().validate(self._source_edit.text(), 0)

    is_valid = Signal(bool)
