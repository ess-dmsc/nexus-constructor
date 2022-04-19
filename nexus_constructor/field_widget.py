import logging
import uuid
from functools import partial
from typing import Any, List, Union

import numpy as np
from PySide2.QtCore import QEvent, QObject, QStringListModel, Qt, Signal
from PySide2.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSizePolicy,
)

from nexus_constructor.array_dataset_table_widget import ArrayDatasetTableWidget
from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.field_attrs import FieldAttrsDialog
from nexus_constructor.invalid_field_names import INVALID_FIELD_NAMES
from nexus_constructor.model.module import Dataset, FileWriterModule, Link
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP, ValueTypes
from nexus_constructor.stream_fields_widget import StreamFieldsWidget
from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import (
    FieldType,
    FieldValueValidator,
    NameValidator,
    UnitValidator,
)
from nexus_constructor.model.group import Group


class FieldNameLineEdit(QLineEdit):
    def __init__(self, possible_field_names: List[str]):
        super().__init__()
        possible_field_names = [
            x for x in possible_field_names if x not in INVALID_FIELD_NAMES
        ]
        self.update_possible_fields(possible_field_names)
        self.setPlaceholderText("Name of new field")
        self.setMinimumWidth(60)
        fix_horizontal_size = QSizePolicy()
        fix_horizontal_size.setHorizontalPolicy(QSizePolicy.Expanding)
        fix_horizontal_size.setHorizontalStretch(3)
        self.setSizePolicy(fix_horizontal_size)

    def focusInEvent(self, event):
        self.completer().complete()
        super(FieldNameLineEdit, self).focusInEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            self.completer().complete()
        else:
            super().keyPressEvent(event)

    def update_possible_fields(self, possible_fields: List[str]):
        self.setCompleter(QCompleter())
        model = QStringListModel()
        model.setStringList(sorted(possible_fields))
        self.completer().setModel(model)


class FieldWidget(QFrame):
    # Used for deletion of field
    something_clicked = Signal()
    enable_3d_value_spinbox = Signal(bool)

    def dataset_type_changed(self, _):
        self.value_line_edit.validator().dataset_type_combo = self.value_type_combo
        self.value_line_edit.validator().field_type_combo = self.field_type_combo
        self.value_line_edit.validator().validate(self.value_line_edit.text(), 0)

    def __init__(
        self,
        node_parent,
        possible_fields=None,
        parent: QListWidget = None,
        parent_dataset: Dataset = None,
        hide_name_field: bool = False,
        show_only_f142_stream: bool = False,
    ):
        super(FieldWidget, self).__init__(parent)

        possible_field_names = []
        self.default_field_types_dict = {}
        self.streams_widget: StreamFieldsWidget = None
        if possible_fields:
            possible_field_names, default_field_types = zip(*possible_fields)
            self.default_field_types_dict = dict(
                zip(possible_field_names, default_field_types)
            )
        self._show_only_f142_stream = show_only_f142_stream
        self._node_parent = node_parent

        self.edit_dialog = QDialog(parent=self)
        self.attrs_dialog = FieldAttrsDialog(parent=self)
        if self.parent() is not None and self.parent().parent() is not None:
            self.parent().parent().destroyed.connect(self.edit_dialog.close)
            self.parent().parent().destroyed.connect(self.attrs_dialog.close)

        self.field_name_edit = FieldNameLineEdit(possible_field_names)
        if self.default_field_types_dict:
            self.field_name_edit.textChanged.connect(self.update_default_type)
        self.hide_name_field = hide_name_field
        if hide_name_field:
            self.name = str(uuid.uuid4())

        self.units_line_edit = QLineEdit()
        self.unit_validator = UnitValidator()
        self.units_line_edit.setValidator(self.unit_validator)
        self.units_line_edit.setMinimumWidth(20)
        self.units_line_edit.setMaximumWidth(50)
        unit_size_policy = QSizePolicy()
        unit_size_policy.setHorizontalPolicy(QSizePolicy.Preferred)
        unit_size_policy.setHorizontalStretch(1)
        self.units_line_edit.setSizePolicy(unit_size_policy)

        self.unit_validator.is_valid.connect(
            partial(validate_line_edit, self.units_line_edit)
        )
        self.units_line_edit.setPlaceholderText(CommonAttrs.UNITS)

        self.field_type_combo: QComboBox = QComboBox()
        self.field_type_combo.addItems([item.value for item in FieldType])
        self.field_type_combo.currentIndexChanged.connect(self.field_type_changed)

        fix_horizontal_size = QSizePolicy()
        fix_horizontal_size.setHorizontalPolicy(QSizePolicy.Fixed)
        self.field_type_combo.setSizePolicy(fix_horizontal_size)

        self.value_type_combo: QComboBox = QComboBox()
        self.value_type_combo.addItems(list(VALUE_TYPE_TO_NP))
        for i, item in enumerate(VALUE_TYPE_TO_NP.keys()):
            if item == ValueTypes.DOUBLE:
                self.value_type_combo.setCurrentIndex(i)
                break
        self.value_type_combo.currentIndexChanged.connect(self.dataset_type_changed)

        self.value_line_edit: QLineEdit = QLineEdit()
        self.value_line_edit.setPlaceholderText("value")

        value_size_policy = QSizePolicy()
        value_size_policy.setHorizontalPolicy(QSizePolicy.Preferred)
        value_size_policy.setHorizontalStretch(2)
        self.value_line_edit.setSizePolicy(value_size_policy)

        self._set_up_value_validator(False)
        self.dataset_type_changed(0)

        self.nx_class_combo = QComboBox()

        self.edit_button = QPushButton("Edit")
        edit_button_size = 50
        self.edit_button.setMaximumSize(edit_button_size, edit_button_size)
        self.edit_button.setSizePolicy(fix_horizontal_size)
        self.edit_button.clicked.connect(self.show_edit_dialog)

        self.attrs_button = QPushButton("Attrs")
        self.attrs_button.setMaximumSize(edit_button_size, edit_button_size)
        self.attrs_button.setSizePolicy(fix_horizontal_size)
        self.attrs_button.clicked.connect(self.show_attrs_dialog)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.field_name_edit)
        self.layout.addWidget(self.field_type_combo)
        self.layout.addWidget(self.value_line_edit)
        self.layout.addWidget(self.nx_class_combo)
        self.layout.addWidget(self.edit_button)
        self.layout.addWidget(self.value_type_combo)
        self.layout.addWidget(self.units_line_edit)
        self.layout.addWidget(self.attrs_button)

        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)

        self.setFrameShadow(QFrame.Raised)
        self.setFrameShape(QFrame.StyledPanel)

        # Allow selecting this field widget in a list by clicking on it's contents
        self.field_name_edit.installEventFilter(self)
        existing_objects = []
        emit = False
        if isinstance(parent, QListWidget):
            for i in range(self.parent().count()):
                new_field_widget = self.parent().itemWidget(self.parent().item(i))
                if new_field_widget is not self and hasattr(new_field_widget, "name"):
                    existing_objects.append(new_field_widget)
        elif isinstance(self._node_parent, Group):
            for child in self._node_parent.children:
                if child is not parent_dataset and hasattr(child, "name"):
                    existing_objects.append(child)
            emit = True
        self._set_up_name_validator(existing_objects=existing_objects)
        self.field_name_edit.validator().is_valid.emit(emit)

        self.value_line_edit.installEventFilter(self)
        self.nx_class_combo.installEventFilter(self)

        # These cause odd double-clicking behaviour when using an event filter so just connecting to the clicked() signals instead.
        self.edit_button.clicked.connect(self.something_clicked)
        self.value_type_combo.highlighted.connect(self.something_clicked)
        self.field_type_combo.highlighted.connect(self.something_clicked)

        # Set the layout for the default field type
        self.field_type_changed()

    def _set_up_name_validator(
        self, existing_objects: List[Union["FieldWidget", FileWriterModule]]
    ):
        self.field_name_edit.setValidator(
            NameValidator(existing_objects, invalid_names=INVALID_FIELD_NAMES)
        )
        self.field_name_edit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self.field_name_edit,
                tooltip_on_accept="Field name is valid.",
                tooltip_on_reject="Field name is not valid",
            )
        )

    @property
    def field_type(self) -> FieldType:
        return FieldType(self.field_type_combo.currentText())

    @field_type.setter
    def field_type(self, field_type: FieldType):
        self.field_type_combo.setCurrentText(field_type.value)
        self.field_type_changed()

    @property
    def name(self) -> str:
        return self.field_name_edit.text()

    @name.setter
    def name(self, name: str):
        self.field_name_edit.setText(name)

    @property
    def dtype(self) -> str:
        return self.value_type_combo.currentText()

    @dtype.setter
    def dtype(self, dtype: str):
        self.value_type_combo.setCurrentText(dtype)

    @property
    def attrs(self):
        return self.value.attributes

    @attrs.setter
    def attrs(self, field: Dataset):
        self.attrs_dialog.fill_existing_attrs(field)

    @property
    def value(self) -> Union[FileWriterModule, None]:
        dtype = self.value_type_combo.currentText()
        return_object: FileWriterModule
        if self.field_type == FieldType.scalar_dataset:
            val = self.value_line_edit.text()
            return_object = Dataset(
                parent_node=self._node_parent,
                name=self.name,
                type=dtype,
                values=val,
            )
        elif self.field_type == FieldType.array_dataset:
            # Squeeze the array so 1D arrays can exist. Should not affect dimensional arrays.
            array = np.squeeze(self.table_view.model.array)
            return_object = Dataset(
                parent_node=self._node_parent,
                name=self.name,
                type=dtype,
                values=array,
            )
        elif self.field_type == FieldType.kafka_stream:
            return_object = self.streams_widget.get_stream_module(self._node_parent)
        elif self.field_type == FieldType.link:
            return_object = Link(
                parent_node=self._node_parent,
                name=self.name,
                source=self.value_line_edit.text(),
            )
        else:
            logging.error(f"unknown field type: {self.name}")
            return None

        if self.field_type != FieldType.link:
            for name, value, dtype in self.attrs_dialog.get_attrs():
                return_object.attributes.set_attribute_value(
                    attribute_name=name,
                    attribute_value=value,
                    attribute_type=dtype,
                )
            if self.units and self.units is not None:
                return_object.attributes.set_attribute_value(
                    CommonAttrs.UNITS, self.units
                )
        return return_object

    @value.setter
    def value(self, value):
        if self.field_type == FieldType.scalar_dataset:
            self.value_line_edit.setText(to_string(value))
        elif self.field_type == FieldType.array_dataset:
            self.table_view.model.array = value
        elif self.field_type == FieldType.link:
            self.value_line_edit.setText(value)

    @property
    def units(self) -> str:
        return self.units_line_edit.text()

    @units.setter
    def units(self, new_units: str):
        self.units_line_edit.setText(new_units)

    def update_default_type(self):
        self.value_type_combo.setCurrentText(
            self.default_field_types_dict.get(self.field_name_edit.text(), "double")
        )

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.MouseButtonPress:
            self.something_clicked.emit()
            return True
        else:
            return False

    def field_type_is_scalar(self) -> bool:
        return self.field_type == FieldType.scalar_dataset

    def field_type_changed(self):
        self.edit_dialog = QDialog(parent=self)
        self._set_up_value_validator(False)
        self.enable_3d_value_spinbox.emit(not self.field_type_is_scalar())

        if self.field_type == FieldType.scalar_dataset:
            self.set_visibility(True, False, False, True)
        elif self.field_type == FieldType.array_dataset:
            self.set_visibility(False, False, True, True)
            self.table_view = ArrayDatasetTableWidget()
        elif self.field_type == FieldType.kafka_stream:
            self.set_visibility(False, False, True, False, show_name_line_edit=True)
            self.streams_widget = StreamFieldsWidget(
                self.edit_dialog, show_only_f142_stream=self._show_only_f142_stream
            )
        elif self.field_type == FieldType.link:
            self.set_visibility(
                True,
                False,
                False,
                False,
                show_unit_line_edit=False,
                show_attrs_edit=False,
            )
            self._set_up_value_validator(False)

    def _set_up_value_validator(self, is_link: bool):
        self.value_line_edit.setValidator(None)
        if is_link:
            return
        else:
            self.value_line_edit.setValidator(
                FieldValueValidator(
                    self.field_type_combo,
                    self.value_type_combo,
                    FieldType.scalar_dataset.value,
                )
            )
            tooltip_on_accept = "Value is cast-able to numpy type."
            tooltip_on_reject = "Value is not cast-able to selected numpy type."

        self.value_line_edit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self.value_line_edit,
                tooltip_on_accept=tooltip_on_accept,
                tooltip_on_reject=tooltip_on_reject,
            )
        )
        self.value_line_edit.validator().validate(self.value_line_edit.text(), None)

    def set_visibility(
        self,
        show_value_line_edit: bool,
        show_nx_class_combo: bool,
        show_edit_button: bool,
        show_value_type_combo: bool,
        show_name_line_edit: bool = True,
        show_attrs_edit: bool = True,
        show_unit_line_edit: bool = True,
    ):
        self.value_line_edit.setVisible(show_value_line_edit)
        self.nx_class_combo.setVisible(show_nx_class_combo)
        self.edit_button.setVisible(show_edit_button)
        self.value_type_combo.setVisible(show_value_type_combo)
        self.units_line_edit.setVisible(show_unit_line_edit)
        self.attrs_button.setVisible(show_attrs_edit)
        self.field_name_edit.setVisible(
            show_name_line_edit and not self.hide_name_field
        )

    def show_edit_dialog(self):
        if self.field_type == FieldType.array_dataset:
            self.edit_dialog.setLayout(QGridLayout())
            self.table_view.model.update_array_dtype(
                VALUE_TYPE_TO_NP[self.value_type_combo.currentText()]
            )
            self.edit_dialog.layout().addWidget(self.table_view)
            self.edit_dialog.setWindowTitle(
                f"Edit {self.value_type_combo.currentText()} Array field"
            )
        elif self.field_type == FieldType.kafka_stream:
            self.edit_dialog.setLayout(QFormLayout())
            self.edit_dialog.layout().addWidget(self.streams_widget)
        if self.edit_dialog.isVisible():
            self.edit_dialog.raise_()
        else:
            self.edit_dialog.show()

    def show_attrs_dialog(self):
        self.attrs_dialog.show()


def to_string(input_to_convert: Any) -> str:
    """
    Converts to string, assumes utf-8 encoding for bytes
    Input can be bytes, str, numpy array
    :param input_to_convert: Dataset value to convert
    :return: str
    """
    if isinstance(input_to_convert, bytes):
        return input_to_convert.decode("utf-8")
    return str(input_to_convert)
