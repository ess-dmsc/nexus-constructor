from functools import partial
from typing import Union

import h5py
from PySide2.QtWidgets import (
    QDialog,
    QGridLayout,
    QListWidget,
    QPushButton,
    QListWidgetItem,
    QLineEdit,
    QFrame,
    QHBoxLayout,
    QComboBox,
)
import numpy as np

from nexus_constructor.array_dataset_table_widget import ArrayDatasetTableWidget
from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import DATASET_TYPE, FieldValueValidator

ATTRS_BLACKLIST = [CommonAttrs.UNITS]


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

        self.layout().addWidget(self.list_widget, 0, 0, 2, 1)
        self.layout().addWidget(self.add_button, 0, 1)
        self.layout().addWidget(self.remove_button, 1, 1)

    def fill_existing_attrs(self, existing_dataset: h5py.Dataset):
        for name, value in existing_dataset.attrs.items():
            if name not in ATTRS_BLACKLIST:
                frame = FieldAttrFrame(name, value)
                self._add_attr(existing_frame=frame)

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
        self.list_widget.setItemWidget(item, frame)

    def _remove_attrs(self):
        for index in self.list_widget.selectedIndexes():
            self.list_widget.takeItem(index.row())

    def get_attrs(self):
        attrs_dict = {}
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            widget = self.list_widget.itemWidget(item)
            attrs_dict[widget.name] = widget.value
        return attrs_dict


class FieldAttrFrame(QFrame):
    def __init__(self, name=None, value=None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setLayout(QHBoxLayout())
        self.attr_name_lineedit = QLineEdit()
        self.attr_value_lineedit = QLineEdit()

        self.array_or_scalar_combo = QComboBox()
        self.array_or_scalar_combo.addItems(["Scalar", "Array"])
        self.array_or_scalar_combo.currentTextChanged.connect(self.type_changed)
        self.array_edit_button = QPushButton("Edit Array")
        self.array_edit_button.clicked.connect(self.show_edit_array_dialog)

        self.attr_dtype_combo = QComboBox()
        self.attr_dtype_combo.addItems([*DATASET_TYPE.keys()])
        self.attr_dtype_combo.currentTextChanged.connect(self.dtype_changed)
        self.dtype_changed(self.attr_dtype_combo.currentText())
        self.dialog = ArrayDatasetTableWidget(self.dtype)

        self.layout().addWidget(self.attr_name_lineedit)
        self.layout().addWidget(self.array_or_scalar_combo)
        self.layout().addWidget(self.attr_dtype_combo)
        self.layout().addWidget(self.attr_value_lineedit)
        self.layout().addWidget(self.array_edit_button)

        self.type_changed("Scalar")

        if name is not None and value is not None:
            self.name = name
            self.value = value

    def type_changed(self, item: str):
        self.attr_value_lineedit.setVisible(item == "Scalar")
        self.array_edit_button.setVisible(item == "Array")
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
    def dtype(self):
        return DATASET_TYPE[self.attr_dtype_combo.currentText()]

    @property
    def is_scalar(self):
        return self.array_or_scalar_combo.currentText() == "Scalar"

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
            if self.dtype == DATASET_TYPE["String"] or isinstance(self.dtype, str):
                return self.attr_value_lineedit.text()
            return self.dtype(self.attr_value_lineedit.text())
        return self.dialog.model.array

    @value.setter
    def value(self, new_value: Union[np.generic, np.ndarray]):
        # Decode the attribute value if it's in byte form
        if isinstance(new_value, bytes):
            new_value = new_value.decode("utf-8")

        self.attr_dtype_combo.setCurrentText(
            "String"
            if isinstance(new_value, str)
            else next(
                key for key, value in DATASET_TYPE.items() if value == new_value.dtype
            )
        )
        if np.isscalar(new_value):
            self.type_changed("Scalar")
            self.attr_value_lineedit.setText(str(new_value))
        else:
            self.type_changed("Array")
            self.dialog.model.array = new_value
        self.dtype_changed(None)
