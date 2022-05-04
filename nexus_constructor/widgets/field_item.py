import logging
import uuid
from functools import partial
from typing import Any, Optional, List, Union

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
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QWidget,
    QLabel,
    QGroupBox
)

# from nexus_constructor.array_dataset_table_widget import ArrayDatasetTableWidget
# from nexus_constructor.common_attrs import CommonAttrs
# from nexus_constructor.field_attrs import FieldAttrsDialog
# from nexus_constructor.invalid_field_names import INVALID_FIELD_NAMES
from nexus_constructor.model import FileWriterModule, Link
from nexus_constructor.widgets.field_name_edit import FieldNameEdit
from nexus_constructor.widgets.scalar_value_edit import ScalarValueEdit
# from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP, ValueTypes
# from nexus_constructor.stream_fields_widget import StreamFieldsWidget
# from nexus_constructor.ui_utils import validate_line_edit

from enum import Enum
from nexus_constructor.model import Dataset
from nexus_constructor.model.module import StreamModule


class ScalarFieldWidget(QWidget):
    def __init__(self, parent: QWidget, module: Dataset):
        super().__init__(parent)
        self._module = module
        self._field_name = FieldNameEdit(parent, module)
        self._scalar_value = ScalarValueEdit(parent, module)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self._field_name)
        self.layout().addWidget(QLabel(parent=parent, text=" : "))
        self.layout().addWidget(self._scalar_value)
        self.layout().setAlignment(Qt.AlignLeft)

# class FieldNameLineEdit(QLineEdit):
#     def __init__(self, possible_field_names: List[str]):
#         super().__init__()
#         possible_field_names = [
#             x for x in possible_field_names if x not in INVALID_FIELD_NAMES
#         ]
#         self.update_possible_fields(possible_field_names)
#         self.setPlaceholderText("Name of new field")
#         self.setMinimumWidth(60)
#         fix_horizontal_size = QSizePolicy()
#         fix_horizontal_size.setHorizontalPolicy(QSizePolicy.Expanding)
#         fix_horizontal_size.setHorizontalStretch(3)
#         self.setSizePolicy(fix_horizontal_size)
#
#     def focusInEvent(self, event):
#         self.completer().complete()
#         super(FieldNameLineEdit, self).focusInEvent(event)
#
#     def keyPressEvent(self, event):
#         if event.key() == Qt.Key_Down:
#             self.completer().complete()
#         else:
#             super().keyPressEvent(event)
#
#     def update_possible_fields(self, possible_fields: List[str]):
#         self.setCompleter(QCompleter())
#         model = QStringListModel()
#         model.setStringList(sorted(possible_fields))
#         self.completer().setModel(model)


class FieldType(Enum):
    scalar_dataset = "Scalar dataset"
    array_dataset = "Array dataset"
    kafka_stream = "Kafka stream"
    link = "Link"


def get_module_type(item: FileWriterModule) -> FieldType:
    if isinstance(item, Dataset):
        if np.isscalar(item.values):
            return FieldType.scalar_dataset
        else:
            return FieldType.array_dataset
    elif isinstance(item, StreamModule):
        return FieldType.kafka_stream
    elif isinstance(item, Link):
        return FieldType.link
    else:
        logging.debug(
            f"Object {item} not handled as field - could be used for other parts of UI instead"
        )
    return None


class FieldItem(QFrame):
    # Used for deletion of field
    # something_clicked = Signal()
    # enable_3d_value_spinbox = Signal(bool)
    #
    # def dataset_type_changed(self, _):
    #     self.value_line_edit.validator().dataset_type_combo = self.value_type_combo
    #     self.value_line_edit.validator().field_type_combo = self.field_type_combo
    #     self.value_line_edit.validator().validate(self.value_line_edit.text(), 0)

    def __init__(
        self,
        parent: QWidget,
        file_writer_module: FileWriterModule,
    ):
        super().__init__(parent)
        self._field_widget: Optional[QWidget] = None
        self._file_writer_module = file_writer_module

    #     self.streams_widget: StreamFieldsWidget = None
    #     if possible_fields:
    #         possible_field_names, default_field_types = zip(*possible_fields)
    #         self.default_field_types_dict = dict(
    #             zip(possible_field_names, default_field_types)
    #         )
    #     self._show_only_f142_stream = show_only_f142_stream
    #     self._node_parent = node_parent
    #
    #     self.edit_dialog = QDialog(parent=self)
    #     self.attrs_dialog = FieldAttrsDialog(parent=self)
    #     if self.parent() is not None and self.parent().parent() is not None:
    #         self.parent().parent().destroyed.connect(self.edit_dialog.close)
    #         self.parent().parent().destroyed.connect(self.attrs_dialog.close)
    #
    #     self.field_name_edit = FieldNameLineEdit(possible_field_names)
    #     if self.default_field_types_dict:
    #         self.field_name_edit.textChanged.connect(self.update_default_type)
    #     self.hide_name_field = hide_name_field
    #     if hide_name_field:
    #         self.name = str(uuid.uuid4())
    #
    #     self.units_line_edit = QLineEdit()
    #     self.unit_validator = UnitValidator()
    #     self.units_line_edit.setValidator(self.unit_validator)
    #     self.units_line_edit.setMinimumWidth(20)
    #     self.units_line_edit.setMaximumWidth(50)
    #     unit_size_policy = QSizePolicy()
    #     unit_size_policy.setHorizontalPolicy(QSizePolicy.Preferred)
    #     unit_size_policy.setHorizontalStretch(1)
    #     self.units_line_edit.setSizePolicy(unit_size_policy)
    #
    #     self.unit_validator.is_valid.connect(
    #         partial(validate_line_edit, self.units_line_edit)
    #     )
    #     self.units_line_edit.setPlaceholderText(CommonAttrs.UNITS)
    #
        self.field_type_combo: QComboBox = QComboBox()
        self.field_type_combo.addItems([item.value for item in FieldType])
        self.field_type_combo.setCurrentText(get_module_type(self._file_writer_module).value)
        self.field_type_combo.currentIndexChanged.connect(self._field_type_changed)

        fix_horizontal_size = QSizePolicy()
        fix_horizontal_size.setHorizontalPolicy(QSizePolicy.Fixed)
        self.field_type_combo.setSizePolicy(fix_horizontal_size)
    #
    #     self.value_type_combo: QComboBox = QComboBox()
    #     self.value_type_combo.addItems(list(VALUE_TYPE_TO_NP))
    #     for i, item in enumerate(VALUE_TYPE_TO_NP.keys()):
    #         if item == ValueTypes.DOUBLE:
    #             self.value_type_combo.setCurrentIndex(i)
    #             break
    #     self.value_type_combo.currentIndexChanged.connect(self.dataset_type_changed)
    #
    #     self.value_line_edit: QLineEdit = QLineEdit()
    #     self.value_line_edit.setPlaceholderText("value")
    #
    #     value_size_policy = QSizePolicy()
    #     value_size_policy.setHorizontalPolicy(QSizePolicy.Preferred)
    #     value_size_policy.setHorizontalStretch(2)
    #     self.value_line_edit.setSizePolicy(value_size_policy)
    #
    #     self._set_up_value_validator(False)
    #     self.dataset_type_changed(0)
    #
    #     self.nx_class_combo = QComboBox()
    #
    #     self.edit_button = QPushButton("Edit")
    #
    #     edit_button_size = 50
    #     self.edit_button.setMaximumSize(edit_button_size, edit_button_size)
    #     self.edit_button.setSizePolicy(fix_horizontal_size)
    #     self.edit_button.clicked.connect(self.show_edit_dialog)
    #
    #     self.attrs_button = QPushButton("Attrs")
    #     self.attrs_button.setMaximumSize(edit_button_size, edit_button_size)
    #     self.attrs_button.setSizePolicy(fix_horizontal_size)
    #     self.attrs_button.clicked.connect(self.show_attrs_dialog)
    #
        self.setLayout(QHBoxLayout())
    #     self.layout.addWidget(self.field_name_edit)
        self.layout().addWidget(self.field_type_combo)
    #     self.layout.addWidget(self.value_line_edit)
    #     self.layout.addWidget(self.nx_class_combo)
    #     self.layout.addWidget(self.edit_button)
    #     self.layout.addWidget(self.value_type_combo)
    #     self.layout.addWidget(self.units_line_edit)
    #     self.layout.addWidget(self.attrs_button)
    #
        self.layout().setAlignment(Qt.AlignLeft)
    #
        self.setFrameShadow(QFrame.Raised)
        self.setFrameShape(QFrame.StyledPanel)
    #
    #     # Allow selecting this field widget in a list by clicking on it's contents
    #     self.field_name_edit.installEventFilter(self)
    #     existing_objects = []
    #     emit = False
    #     if isinstance(parent, QListWidget):
    #         for i in range(self.parent().count()):
    #             new_field_widget = self.parent().itemWidget(self.parent().item(i))
    #             if new_field_widget is not self and hasattr(new_field_widget, "name"):
    #                 existing_objects.append(new_field_widget)
    #     elif isinstance(self._node_parent, Group):
    #         for child in self._node_parent.children:
    #             if child is not parent_dataset and hasattr(child, "name"):
    #                 existing_objects.append(child)
    #         emit = True
    #     self._set_up_name_validator(existing_objects=existing_objects)
    #     self.field_name_edit.validator().is_valid.emit(emit)
    #
    #     self.value_line_edit.installEventFilter(self)
    #     self.nx_class_combo.installEventFilter(self)
    #
    #     # These cause odd double-clicking behaviour when using an event filter so just connecting to the clicked() signals instead.
    #     self.edit_button.clicked.connect(self.something_clicked)
    #     self.value_type_combo.highlighted.connect(self.something_clicked)
    #     self.field_type_combo.highlighted.connect(self.something_clicked)
    #
    #     # Set the layout for the default field type
        self._field_type_changed()
    #
    # def _set_up_name_validator(
    #     self, existing_objects: List[Union["FieldWidget", FileWriterModule]]
    # ):
    #     self.field_name_edit.setValidator(
    #         NameValidator(existing_objects, invalid_names=INVALID_FIELD_NAMES)
    #     )
    #     self.field_name_edit.validator().is_valid.connect(
    #         partial(
    #             validate_line_edit,
    #             self.field_name_edit,
    #             tooltip_on_accept="Field name is valid.",
    #             tooltip_on_reject="Field name is not valid",
    #         )
    #     )
    #
    # @property
    # def field_type(self) -> FieldType:
    #     return FieldType(self.field_type_combo.currentText())
    #
    # @field_type.setter
    # def field_type(self, field_type: FieldType):
    #     self.field_type_combo.setCurrentText(field_type.value)
    #     self.field_type_changed()
    #
    # @property
    # def name(self) -> str:
    #     return self.field_name_edit.text()
    #
    # @name.setter
    # def name(self, name: str):
    #     self.field_name_edit.setText(name)
    #
    # @property
    # def dtype(self) -> str:
    #     return self.value_type_combo.currentText()
    #
    # @dtype.setter
    # def dtype(self, dtype: str):
    #     self.value_type_combo.setCurrentText(dtype)
    #
    # @property
    # def attrs(self):
    #     return self.value.attributes
    #
    # @attrs.setter
    # def attrs(self, field: Dataset):
    #     self.attrs_dialog.fill_existing_attrs(field)
    #
    # @value.setter
    # def value(self, value):
    #     if self.field_type == FieldType.scalar_dataset:
    #         self.value_line_edit.setText(to_string(value))
    #     elif self.field_type == FieldType.array_dataset:
    #         self.table_view.model.array = value
    #     elif self.field_type == FieldType.link:
    #         self.value_line_edit.setText(value)
    #
    # @property
    # def units(self) -> str:
    #     return self.units_line_edit.text()
    #
    # @units.setter
    # def units(self, new_units: str):
    #     self.units_line_edit.setText(new_units)
    #
    # def update_default_type(self):
    #     self.value_type_combo.setCurrentText(
    #         self.default_field_types_dict.get(self.field_name_edit.text(), "double")
    #     )
    #
    # def eventFilter(self, watched: QObject, event: QEvent) -> bool:
    #     if event.type() == QEvent.MouseButtonPress:
    #         self.something_clicked.emit()
    #         return True
    #     else:
    #         return False
    #
    # def field_type_is_scalar(self) -> bool:
    #     return self.field_type == FieldType.scalar_dataset
    #


    def _remove_existing_widget(self):
        if self._field_widget is not None:
            self.layout().removeWidget(self._field_widget)

    def _instantiate_scalar_widgets(self):
        self._remove_existing_widget()
        self._field_widget = ScalarFieldWidget(self.parent(), self._file_writer_module)
        self.layout().addWidget(self._field_widget)

    def _instantiate_array_widgets(self):
        self._remove_existing_widget()

    def _instantiate_stream_widgets(self):
        self._remove_existing_widget()

    def _instantiate_link_widgets(self):
        self._remove_existing_widget()

    def _field_type_changed(self):
        populate_widget_map = {FieldType.scalar_dataset.value: self._instantiate_scalar_widgets, FieldType.array_dataset.value: self._instantiate_array_widgets, FieldType.kafka_stream.value: self._instantiate_stream_widgets, FieldType.link.value: self._instantiate_link_widgets}

        populate_widget_map[self.field_type_combo.currentText()]()
    #     self.edit_dialog = QDialog(parent=self)
    #     self.edit_dialog.setModal(True)
    #     self._set_up_value_validator(False)
    #     self.enable_3d_value_spinbox.emit(not self.field_type_is_scalar())
    #
    #     if self.field_type == FieldType.scalar_dataset:
    #         self.set_visibility(True, False, False, True)
    #     elif self.field_type == FieldType.array_dataset:
    #         self.set_visibility(False, False, True, True)
    #         self.table_view = ArrayDatasetTableWidget()
    #     elif self.field_type == FieldType.kafka_stream:
    #         self.set_visibility(False, False, True, False, show_name_line_edit=True)
    #         self.streams_widget = StreamFieldsWidget(
    #             self.edit_dialog, show_only_f142_stream=self._show_only_f142_stream
    #         )
    #     elif self.field_type == FieldType.link:
    #         self.set_visibility(
    #             True,
    #             False,
    #             False,
    #             False,
    #             show_unit_line_edit=False,
    #             show_attrs_edit=False,
    #         )
    #         self._set_up_value_validator(False)
    #
    # def _set_up_value_validator(self, is_link: bool):
    #     self.value_line_edit.setValidator(None)
    #     if is_link:
    #         return
    #     else:
    #         self.value_line_edit.setValidator(
    #             FieldValueValidator(
    #                 self.field_type_combo,
    #                 self.value_type_combo,
    #                 FieldType.scalar_dataset.value,
    #             )
    #         )
    #         tooltip_on_accept = "Value is cast-able to numpy type."
    #         tooltip_on_reject = "Value is not cast-able to selected numpy type."
    #
    #     self.value_line_edit.validator().is_valid.connect(
    #         partial(
    #             validate_line_edit,
    #             self.value_line_edit,
    #             tooltip_on_accept=tooltip_on_accept,
    #             tooltip_on_reject=tooltip_on_reject,
    #         )
    #     )
    #     self.value_line_edit.validator().validate(self.value_line_edit.text(), None)
    #
    # def set_visibility(
    #     self,
    #     show_value_line_edit: bool,
    #     show_nx_class_combo: bool,
    #     show_edit_button: bool,
    #     show_value_type_combo: bool,
    #     show_name_line_edit: bool = True,
    #     show_attrs_edit: bool = True,
    #     show_unit_line_edit: bool = True,
    # ):
    #     self.value_line_edit.setVisible(show_value_line_edit)
    #     self.nx_class_combo.setVisible(show_nx_class_combo)
    #     self.edit_button.setVisible(show_edit_button)
    #     self.value_type_combo.setVisible(show_value_type_combo)
    #     self.units_line_edit.setVisible(show_unit_line_edit)
    #     self.attrs_button.setVisible(show_attrs_edit)
    #     self.field_name_edit.setVisible(
    #         show_name_line_edit and not self.hide_name_field
    #     )
    #
    # def show_edit_dialog(self):
    #     if self.field_type == FieldType.array_dataset:
    #         self.edit_dialog.setLayout(QGridLayout())
    #         self.table_view.model.update_array_dtype(
    #             VALUE_TYPE_TO_NP[self.value_type_combo.currentText()]
    #         )
    #         self.edit_dialog.layout().addWidget(self.table_view)
    #         self.edit_dialog.setWindowTitle(
    #             f"Edit {self.value_type_combo.currentText()} Array field"
    #         )
    #     elif self.field_type == FieldType.kafka_stream:
    #         self.edit_dialog.setLayout(QFormLayout())
    #         self.edit_dialog.layout().addWidget(self.streams_widget)
    #     if self.edit_dialog.isVisible():
    #         self.edit_dialog.raise_()
    #     else:
    #         self.edit_dialog.show()
    #
    # def show_attrs_dialog(self):
    #     self.attrs_dialog.show()


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
