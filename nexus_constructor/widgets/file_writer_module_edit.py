from functools import partial

from PySide2.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QComboBox, QPushButton
from PySide2.QtCore import Signal, Qt

from nexus_constructor.model.module import StreamModule, StreamModules
from nexus_constructor.model.writer_module_container import ModuleContainer
from nexus_constructor.ui_utils import line_edit_validation_result_handler
from nexus_constructor.validators import NoEmptyStringValidator, MultiItemValidator


class FileWriterModuleEdit(QWidget):
    def __init__(self, parent: QWidget, module: StreamModule):
        super().__init__(parent)
        self._module_container = ModuleContainer(module)
        self.setLayout(QHBoxLayout())
        self._module_type_combo: QComboBox = QComboBox(self)
        self._module_type_combo.addItems([m.value for m in StreamModules])
        self._module_type_combo.setCurrentText(module.writer_module)

        self._topic_edit = QLineEdit(self)
        self._topic_edit.setValidator(NoEmptyStringValidator())
        self._source_edit = QLineEdit(self)
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

    def check_validity(self):
        self._topic_edit.validator().validate(self._topic_edit.text(), 0)
        self._source_edit.validator().validate(self._source_edit.text(), 0)

    is_valid = Signal(bool)
