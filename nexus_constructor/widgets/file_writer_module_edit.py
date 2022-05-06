from functools import partial

from PySide2.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QComboBox
from PySide2.QtCore import Signal, Qt

from nexus_constructor.model.module import FileWriterModule
from nexus_constructor.model.writer_module_container import ModuleContainer
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP, ValueTypes
from nexus_constructor.ui_utils import line_edit_validation_result_handler
from nexus_constructor.validators import UnitValidator
from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.validators import MultiItemValidator


class FileWriterModuleEdit(QWidget):
    def __init__(self, parent: QWidget, module: FileWriterModule):
        super().__init__(parent)
        self._module_container = ModuleContainer(module)
        self.setLayout(QHBoxLayout())
        self._value_type_combo: QComboBox = QComboBox(self)
        self._value_type_combo.addItems(list(VALUE_TYPE_TO_NP))
        self._value_type_combo.setCurrentText(ValueTypes.DOUBLE)
        self._units_line_edit = QLineEdit(self)
        self._units_line_edit.setValidator(UnitValidator())

        self._validator = MultiItemValidator()
        self._units_line_edit.validator().is_valid.connect(
            partial(self._validator.set_is_valid, self._units_line_edit)
        )
        self._validator.is_valid.connect(self.is_valid.emit)

        self._units_line_edit.validator().is_valid.connect(
            partial(line_edit_validation_result_handler, self._units_line_edit)
        )

        self._units_line_edit.setPlaceholderText("unit")
        self._units_line_edit.setMaximumWidth(20)
        self._units_line_edit.setMaximumWidth(50)

        self.layout().addWidget(self._value_type_combo)
        self.layout().addWidget(self._units_line_edit)

        self.layout().setAlignment(Qt.AlignLeft)

        self._value_type_combo.currentIndexChanged.connect(self._dataset_type_changed)
        self._units_line_edit.textEdited.connect(self._unit_changed)

        if self._dataset.attributes.contains_attribute(CommonAttrs.UNITS):
            self._units_line_edit.setText(
                self._dataset.attributes.get_attribute_value(CommonAttrs.UNITS)
            )
        self._value_type_combo.setCurrentText(
            ValueTypes.STRING if not self._dataset.type else self._dataset.type
        )
        self._units_line_edit.setText(
            self._dataset.attributes.get_attribute_value(CommonAttrs.UNITS)
        )

    def _unit_changed(self, new_unit: str):
        if not new_unit:
            if self._dataset.attributes.contains_attribute(CommonAttrs.UNITS):
                self._dataset.attributes.remove_attribute(CommonAttrs.UNITS)
            return
        self._dataset.attributes.set_attribute_value(CommonAttrs.UNITS, new_unit)

    def check_validity(self):
        self._units_line_edit.validator().validate(self._units_line_edit.text(), 0)

    is_valid = Signal(bool)
