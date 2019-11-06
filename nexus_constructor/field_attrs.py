from typing import Union
from PySide2.QtWidgets import (
    QDialog,
    QGridLayout,
    QListWidget,
    QPushButton,
    QLayout,
    QListWidgetItem,
    QLineEdit,
    QFrame,
    QHBoxLayout,
    QComboBox,
)
import numpy as np

from nexus_constructor.validators import DATASET_TYPE


class FieldAttrsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QGridLayout())
        self.setWindowTitle("Edit Attributes")

        self.list_widget = QListWidget()
        self.list_widget.setMinimumSize(800, 600)
        self.add_button = QPushButton("Add attr")
        self.add_button.clicked.connect(self._add_attr)
        self.remove_button = QPushButton("Remove attr")
        self.remove_button.clicked.connect(self._remove_attrs)

        self.layout().addWidget(self.list_widget, 0, 0, 2, 1)
        self.layout().addWidget(self.add_button, 0, 1)
        self.layout().addWidget(self.remove_button, 1, 1)

    def _add_attr(self):
        item = QListWidgetItem()
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, FieldAttrFrame())

    def _remove_attrs(self):
        for index in self.list_widget.selectedIndexes():
            self.list_widget.takeItem(index.row())


class FieldAttrFrame(QFrame):
    def __init__(self, parent=None, name=None, value=None):
        super().__init__(parent)
        self.array = []
        self.setMinimumHeight(40)
        self.setLayout(QHBoxLayout())
        self.attr_name_lineedit = QLineEdit()
        self.attr_value_lineedit = QLineEdit()
        self.attr_type_combo = QComboBox()
        self.attr_type_combo.addItems([*DATASET_TYPE.keys()])

        self.array_or_scalar_combo = QComboBox()
        self.array_or_scalar_combo.addItems(["Scalar", "Array"])
        self.array_or_scalar_combo.currentTextChanged.connect(self.type_changed)
        self.array_edit_button = QPushButton("Edit Array")
        self.array_edit_button.clicked.connect(self.edit_array)

        self.layout().addWidget(self.attr_name_lineedit)
        self.layout().addWidget(self.array_or_scalar_combo)
        self.layout().addWidget(self.attr_type_combo)
        self.layout().addWidget(self.attr_value_lineedit)
        self.layout().addWidget(self.array_edit_button)

        self.type_changed("Scalar")

        if name and value:
            self.value(name, value)

    def type_changed(self, item: str):
        self.attr_value_lineedit.setVisible(item == "Scalar")
        self.array_edit_button.setVisible(item == "Array")

    def edit_array(self, _):
        pass

    @property
    def value(self) -> Union[str, Union[np.generic, np.ndarray]]:
        pass

    @value.setter
    def value(self, new_name: str, new_value: Union[np.generic, np.ndarray]):
        self.attr_name_lineedit.setText(new_name)
        if np.isscalar(new_value):
            self.attr_value_lineedit.setText(str(new_value))
        else:
            pass  # fill in array - not sure how to do this yet
