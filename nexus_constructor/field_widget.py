import logging
import uuid
import numpy as np
import h5py
from functools import partial
from PySide2.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QFrame,
    QComboBox,
    QDialog,
    QListWidget,
    QGridLayout,
    QFormLayout,
)
from PySide2.QtWidgets import QCompleter, QLineEdit, QSizePolicy
from PySide2.QtCore import QStringListModel, Qt, Signal, QEvent, QObject
from typing import List, Union
from nexus_constructor.array_dataset_table_widget import ArrayDatasetTableWidget
from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.field_attrs import FieldAttrsDialog
from nexus_constructor.invalid_field_names import INVALID_FIELD_NAMES
from nexus_constructor.nexus.nexus_wrapper import (
    create_temporary_in_memory_file,
    to_string,
)
from nexus_constructor.stream_fields_widget import StreamFieldsWidget
from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import (
    FieldValueValidator,
    FieldType,
    DATASET_TYPE,
    NameValidator,
    HDFLocationExistsValidator,
    UnitValidator,
)


class FieldNameLineEdit(QLineEdit):
    def __init__(self, possible_field_names: List[str]):
        super().__init__()
        possible_field_names = [
            x for x in possible_field_names if x not in INVALID_FIELD_NAMES
        ]
        self.update_possible_fields(possible_field_names)
        self.setPlaceholderText("Name of new field")
        self.setMinimumWidth(160)
        fix_horizontal_size = QSizePolicy()
        fix_horizontal_size.setHorizontalPolicy(QSizePolicy.Fixed)
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
        model.setStringList(possible_fields)
        self.completer().setModel(model)


class FieldWidget(QFrame):
    # Used for deletion of field
    something_clicked = Signal()

    def dataset_type_changed(self, _):
        self.value_line_edit.validator().dataset_type_combo = self.value_type_combo
        self.value_line_edit.validator().field_type_combo = self.field_type_combo
        self.value_line_edit.validator().validate(self.value_line_edit.text(), 0)

    def __init__(
        self,
        possible_field_names=None,
        parent: QListWidget = None,
        instrument: "Instrument" = None,  # noqa: F821
        hide_name_field: bool = False,
    ):
        super(FieldWidget, self).__init__(parent)

        if possible_field_names is None:
            possible_field_names = []

        self.edit_dialog = QDialog(parent=self)
        self.attrs_dialog = FieldAttrsDialog(parent=self)
        self.instrument = instrument

        self.field_name_edit = FieldNameLineEdit(possible_field_names)
        self.hide_name_field = hide_name_field
        if hide_name_field:
            self.name = str(uuid.uuid4())

        self.units_line_edit = QLineEdit()
        self.unit_validator = UnitValidator()
        self.units_line_edit.setValidator(self.unit_validator)

        self.unit_validator.is_valid.connect(
            partial(validate_line_edit, self.units_line_edit)
        )
        self.units_line_edit.setPlaceholderText(CommonAttrs.UNITS)

        self.field_type_combo = QComboBox()
        self.field_type_combo.addItems([item.value for item in FieldType])
        self.field_type_combo.currentIndexChanged.connect(self.field_type_changed)

        fix_horizontal_size = QSizePolicy()
        fix_horizontal_size.setHorizontalPolicy(QSizePolicy.Fixed)
        self.field_type_combo.setSizePolicy(fix_horizontal_size)

        self.value_type_combo = QComboBox()
        self.value_type_combo.addItems(list(DATASET_TYPE.keys()))
        self.value_type_combo.currentIndexChanged.connect(self.dataset_type_changed)

        self.value_line_edit = QLineEdit()
        self.value_line_edit.setPlaceholderText("value")

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
        if parent is not None:
            self._set_up_name_validator()
            self.field_name_edit.validator().is_valid.emit(False)

        self.value_line_edit.installEventFilter(self)
        self.nx_class_combo.installEventFilter(self)

        # These cause odd double-clicking behaviour when using an event filter so just connecting to the clicked() signals instead.
        self.edit_button.clicked.connect(self.something_clicked)
        self.value_type_combo.highlighted.connect(self.something_clicked)
        self.field_type_combo.highlighted.connect(self.something_clicked)

        # Set the layout for the default field type
        self.field_type_changed()

    def _set_up_name_validator(self):
        field_widgets = []
        for i in range(self.parent().count()):
            field_widgets.append(self.parent().itemWidget(self.parent().item(i)))

        self.field_name_edit.setValidator(
            NameValidator(field_widgets, invalid_names=INVALID_FIELD_NAMES)
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
    def field_type(self, field_type: str):
        self.field_type_combo.setCurrentText(field_type)
        self.field_type_changed()

    @property
    def name(self) -> str:
        return self.field_name_edit.text()

    @name.setter
    def name(self, name: str):
        self.field_name_edit.setText(name)

    @property
    def dtype(self) -> Union[h5py.Datatype, h5py.SoftLink, h5py.Group]:
        if self.field_type == FieldType.scalar_dataset:
            return self.value.dtype
        if self.field_type == FieldType.array_dataset:
            return self.table_view.model.array.dtype
        if self.field_type == FieldType.link:
            return h5py.SoftLink
        if self.field_type == FieldType.kafka_stream:
            return h5py.Group

    @dtype.setter
    def dtype(self, dtype: h5py.Datatype):
        type_map = {np.object: "String", np.float64: "Float", np.int64: "Integer"}
        for item in type_map.keys():
            if dtype == item:
                self.value_type_combo.setCurrentText(type_map[item])
                return
        self.value_type_combo.setCurrentText(
            next(key for key, value in DATASET_TYPE.items() if value == dtype)
        )

    @property
    def attrs(self) -> h5py.Dataset.attrs:
        return self.value.attrs

    @attrs.setter
    def attrs(self, field: h5py.Dataset):
        self.attrs_dialog.fill_existing_attrs(field)

    @property
    def value(self) -> Union[h5py.Dataset, h5py.Group, h5py.SoftLink]:
        return_object = None
        if self.field_type == FieldType.scalar_dataset:
            dtype = DATASET_TYPE[self.value_type_combo.currentText()]
            val = self.value_line_edit.text()
            if dtype == h5py.special_dtype(vlen=str):
                return_object = create_temporary_in_memory_file().create_dataset(
                    name=self.name, dtype=dtype, data=val
                )
            else:
                return_object = create_temporary_in_memory_file().create_dataset(
                    name=self.name, dtype=dtype, data=dtype(val)
                )
        elif self.field_type == FieldType.array_dataset:
            # Squeeze the array so 1D arrays can exist. Should not affect dimensional arrays.
            return_object = create_temporary_in_memory_file().create_dataset(
                name=self.name, data=np.squeeze(self.table_view.model.array)
            )
        elif self.field_type == FieldType.kafka_stream:
            return_object = self.streams_widget.get_stream_group()
        elif self.field_type == FieldType.link:
            return_object = h5py.SoftLink(self.value_line_edit.text())
        else:
            logging.error(f"unknown field type: {self.name}")
        if self.field_type != FieldType.link:
            for attr_name, attr_value in self.attrs_dialog.get_attrs().items():
                self.instrument.nexus.set_attribute_value(
                    return_object, attr_name, attr_value
                )
            if self.units and self.units is not None:
                self.instrument.nexus.set_attribute_value(
                    return_object, CommonAttrs.UNITS, self.units
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
    def units(self):
        return self.units_line_edit.text()

    @units.setter
    def units(self, new_units):
        self.units_line_edit.setText(new_units)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.MouseButtonPress:
            self.something_clicked.emit()
            return True
        else:
            return False

    def field_type_changed(self):
        self.edit_dialog = QDialog(parent=self)
        self._set_up_value_validator(False)
        if self.field_type == FieldType.scalar_dataset:
            self.set_visibility(True, False, False, True)
        elif self.field_type == FieldType.array_dataset:
            self.set_visibility(False, False, True, True)
            self.table_view = ArrayDatasetTableWidget()
        elif self.field_type == FieldType.kafka_stream:
            self.set_visibility(False, False, True, False, show_name_line_edit=True)
            self.streams_widget = StreamFieldsWidget(self.edit_dialog)
        elif self.field_type == FieldType.link:
            self.set_visibility(True, False, False, False)
            self._set_up_value_validator(True)
        elif self.field_type == FieldType.nx_class:
            self.set_visibility(False, True, False, False)

    def _set_up_value_validator(self, is_link: bool):
        self.value_line_edit.setValidator(None)
        if is_link:
            self.value_line_edit.setValidator(
                HDFLocationExistsValidator(
                    self.instrument.nexus.nexus_file, self.field_type_combo
                )
            )

            tooltip_on_accept = "Valid HDF path"
            tooltip_on_reject = "HDF Path is not valid"
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
    ):
        self.value_line_edit.setVisible(show_value_line_edit)
        self.nx_class_combo.setVisible(show_nx_class_combo)
        self.edit_button.setVisible(show_edit_button)
        self.value_type_combo.setVisible(show_value_type_combo)
        self.field_name_edit.setVisible(
            show_name_line_edit and not self.hide_name_field
        )

    def show_edit_dialog(self):
        if self.field_type == FieldType.array_dataset:
            self.edit_dialog.setLayout(QGridLayout())
            self.table_view.model.update_array_dtype(
                DATASET_TYPE[self.value_type_combo.currentText()]
            )
            self.edit_dialog.layout().addWidget(self.table_view)
            self.edit_dialog.setWindowTitle(
                f"Edit {self.value_type_combo.currentText()} Array field"
            )
        elif self.field_type == FieldType.kafka_stream:
            self.edit_dialog.setLayout(QFormLayout())
            self.edit_dialog.layout().addWidget(self.streams_widget)
        elif self.field_type.currentText() == FieldType.nx_class:
            # TODO: show nx class panels
            pass
        self.edit_dialog.show()

    def show_attrs_dialog(self):
        self.attrs_dialog.show()
