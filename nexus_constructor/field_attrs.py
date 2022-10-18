from functools import partial
from typing import Any, List, Union

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
)

from nexus_constructor.array_dataset_table_widget import ArrayDatasetTableWidget
from nexus_constructor.common_attrs import ARRAY, SCALAR, CommonAttrs
from nexus_constructor.model import Group
from nexus_constructor.model.module import FileWriterModule
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP, ValueTypes
from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import AttributeNameValidator, FieldValueValidator

ATTRS_EXCLUDELIST = [CommonAttrs.UNITS]


def _get_human_readable_type(new_value: Any):
    if isinstance(new_value, str):
        return ValueTypes.STRING
    elif isinstance(new_value, int):
        return ValueTypes.INT
    elif isinstance(new_value, float):
        return ValueTypes.DOUBLE
    else:
        try:
            return next(
                key
                for key, value in VALUE_TYPE_TO_NP.items()
                if value == new_value.dtype
            )
        except AttributeError:
            return None


class FieldAttrsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QGridLayout())
        self.setWindowTitle("Edit Attributes")

        self.list_widget = QListWidget()
        self.list_widget.setMinimumSize(800, 600)
        self.add_button = QPushButton("Add attr")
        self.add_button.clicked.connect(self.__add_attr)
        self.remove_button = QPushButton("Remove attr")
        self.remove_button.clicked.connect(self._remove_attrs)
        self.close_button = QPushButton("OK")
        self.close_button.clicked.connect(self.close)

        self.layout().addWidget(self.list_widget, 0, 0, 3, 1)
        self.layout().addWidget(self.add_button, 0, 1)
        self.layout().addWidget(self.remove_button, 1, 1)
        self.layout().addWidget(self.close_button, 2, 1)

    def fill_existing_attrs(
        self,
        existing_dataset: Union[FileWriterModule, Group],
        attributes_exclude: List = ATTRS_EXCLUDELIST,
    ):
        for attr in existing_dataset.attributes:
            if attr.name not in attributes_exclude:
                frame = FieldAttrFrame(attr)
                self._add_attr(existing_frame=frame)

    def add_update_signal(self):
        self.close_button.clicked.connect(self.update_attributes)

    def __add_attr(self):
        """
        Only used for button presses. Any additional arguments from the signal are ignored.
        """
        self._add_attr()

    def _add_attr(self, existing_frame=None):
        item = QListWidgetItem()
        self.list_widget.addItem(item)
        frame = existing_frame if existing_frame is not None else FieldAttrFrame()
        item.setSizeHint(frame.sizeHint())
        self._setup_attribute_name_validator(frame)
        self.list_widget.setItemWidget(item, frame)

    def _remove_attrs(self):
        for index in self.list_widget.selectedIndexes():
            self.list_widget.takeItem(index.row())

    def update_attributes(self):
        self.update_attributes_signal.emit(self.get_attrs())

    def set_view_only(self, label: str, set_visibility: bool):
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            widget = self.list_widget.itemWidget(item)
            widget.array_edit_button.setText(label)
            widget.dialog.add_row_button.setVisible(set_visibility)
            widget.dialog.remove_row_button.setVisible(set_visibility)
            widget.dialog.add_column_button.setVisible(set_visibility)
            widget.dialog.remove_column_button.setVisible(set_visibility)

    def get_attrs(self):
        attrs_list = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            widget = self.list_widget.itemWidget(item)
            if widget:
                attrs_list.append((widget.name, widget.value, widget.dtype))
        return attrs_list

    def get_attr_names(self):
        return [item[0] for item in self.get_attrs()]

    def _setup_attribute_name_validator(self, frame):
        frame.attr_name_lineedit.setValidator(
            AttributeNameValidator(self.get_attr_names)
        )
        frame.attr_name_lineedit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                frame.attr_name_lineedit,
                tooltip_on_accept="Attribute name is valid.",
                tooltip_on_reject="Attribute name is not valid",
            )
        )

    update_attributes_signal = Signal(tuple)


class FieldAttrFrame(QFrame):
    def __init__(self, attr=None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setLayout(QHBoxLayout())
        self.attr_name_lineedit = QLineEdit()
        self.attr_value_lineedit = QLineEdit()

        self.array_or_scalar_combo = QComboBox()
        self.array_or_scalar_combo.addItems([SCALAR, ARRAY])
        self.array_or_scalar_combo.currentTextChanged.connect(self.type_changed)
        self.array_edit_button = QPushButton("Edit Array")
        self.array_edit_button.clicked.connect(self.show_edit_array_dialog)

        self.attr_dtype_combo = QComboBox()
        self.attr_dtype_combo.addItems([*VALUE_TYPE_TO_NP.keys()])
        for i, item in enumerate(VALUE_TYPE_TO_NP.keys()):
            if item == ValueTypes.DOUBLE:
                self.attr_dtype_combo.setCurrentIndex(i)
                break
        self.attr_dtype_combo.currentTextChanged.connect(self.dtype_changed)
        self.dtype_changed(self.attr_dtype_combo.currentText())
        self.dialog = ArrayDatasetTableWidget(VALUE_TYPE_TO_NP[self.dtype])

        self.layout().addWidget(self.attr_name_lineedit)
        self.layout().addWidget(self.array_or_scalar_combo)
        self.layout().addWidget(self.attr_dtype_combo)
        self.layout().addWidget(self.attr_value_lineedit)
        self.layout().addWidget(self.array_edit_button)

        self.type_changed(SCALAR)

        if attr is not None:
            self.name = attr.name
            self.value = attr.values
            self.dtype = attr.type

    def type_changed(self, item: str):
        self.attr_value_lineedit.setVisible(item == SCALAR)
        self.array_edit_button.setVisible(item == ARRAY)
        self.array_or_scalar_combo.setCurrentText(item)

    def dtype_changed(self, _: str):
        self.attr_value_lineedit.setValidator(
            FieldValueValidator(self.array_or_scalar_combo, self.attr_dtype_combo)
        )
        self.attr_value_lineedit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self.attr_value_lineedit,
                tooltip_on_accept="Value is cast-able to numpy type.",
                tooltip_on_reject="Value is not cast-able to selected numpy type.",
            )
        )
        self.attr_value_lineedit.validator().validate(
            self.attr_value_lineedit.text(), 0
        )

    @property
    def dtype(self) -> str:
        return self.attr_dtype_combo.currentText()

    @dtype.setter
    def dtype(self, new_dtype: str):
        self.attr_dtype_combo.setCurrentText(new_dtype)

    @property
    def is_scalar(self):
        return self.array_or_scalar_combo.currentText() == SCALAR

    def show_edit_array_dialog(self, _):
        self.dialog.show()

    @property
    def name(self):
        return self.attr_name_lineedit.text()

    @name.setter
    def name(self, new_name: str):
        self.attr_name_lineedit.setText(new_name)

    @property
    def value(self) -> Union[np.generic, np.ndarray]:
        if self.is_scalar:
            if self.dtype == ValueTypes.STRING:
                return self.attr_value_lineedit.text()
            value = self.attr_value_lineedit.text()
            type_cast = VALUE_TYPE_TO_NP[self.attr_dtype_combo.currentText()]
            return type_cast(value) if value else ""
        return np.squeeze(self.dialog.model.array)

    @value.setter
    def value(self, new_value: np.ndarray):
        # Decode the attribute value if it's in byte form
        if isinstance(new_value, bytes):
            new_value = new_value.decode("utf-8")

        self.attr_dtype_combo.setCurrentText(_get_human_readable_type(new_value))
        if np.isscalar(new_value):
            self.type_changed(SCALAR)
            self.attr_value_lineedit.setText(str(new_value))
        else:
            self.type_changed(ARRAY)
            self.dialog.model.array = new_value
            try:
                self.dialog.model.update_array_dtype(new_value.dtype)
            except AttributeError:
                pass
        self.dtype_changed(None)
