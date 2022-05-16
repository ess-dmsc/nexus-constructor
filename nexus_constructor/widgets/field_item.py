import logging
from typing import Any, Optional
from functools import partial

import numpy as np
from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
    QLabel,
    QPushButton,
)

from nexus_constructor.model import FileWriterModule, Link
from nexus_constructor.widgets.field_name_edit import FieldNameEdit
from nexus_constructor.widgets.scalar_value_edit import ScalarValueEdit
from nexus_constructor.widgets.scalar_array_edit import ScalarArrayEdit
from nexus_constructor.widgets.link_edit import LinkEdit
from nexus_constructor.widgets.file_writer_module_edit import FileWriterModuleEdit
from nexus_constructor.validators import MultiItemValidator
from nexus_constructor.field_attrs import FieldAttrsDialog

from enum import Enum
from nexus_constructor.model import Dataset
from nexus_constructor.model.module import StreamModule, F142Stream
from nexus_constructor.model.writer_module_container import ModuleContainer


class BaseFieldWidget(QWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent)
        self._container = container
        self._validator = MultiItemValidator()
        self.setLayout(QHBoxLayout())
        self._validator.is_valid.connect(self.is_valid.emit)

    is_valid = Signal(bool)


class BaseScalarFieldWidget(BaseFieldWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent, container)
        if not isinstance(container.module, Dataset):
            parent_node = container.module.parent_node
            new_module = Dataset(parent_node=parent_node, name="", values=0)
            parent_node.children[
                parent_node.children.index(container.module)
            ] = new_module
            container.module = new_module
        self._container = container
        self._field_name = FieldNameEdit(parent, container.module)
        self._attrs_dialog = FieldAttrsDialog(parent=parent)
        self._attrs_dialog.accepted.connect(self._done_with_attributes)
        edit_button_size = 50

        self._attrs_button = QPushButton("Attrs")
        self._attrs_button.setMaximumSize(edit_button_size, edit_button_size)
        self._attrs_button.clicked.connect(self._show_attrs_dialog)
        self.layout().addWidget(self._field_name)
        self.layout().addWidget(QLabel(parent=parent, text=" : "))
        self.layout().addWidget(self._attrs_button)
        self.layout().setAlignment(Qt.AlignLeft)
        self._field_name.is_valid.connect(
            partial(self._validator.set_is_valid, self._field_name)
        )

    def _done_with_attributes(self):
        for name, value, dtype in self._attrs_dialog.get_attrs():
            if self._module.attributes.contains_attribute(name):
                self._module.attributes.remove_attribute(name)
            self._module.attributes.set_attribute_value(
                attribute_name=name,
                attribute_value=value,
                attribute_type=dtype,
            )

    def _show_attrs_dialog(self):
        self._attrs_dialog._remove_attrs()
        self._attrs_dialog.fill_existing_attrs(self._module)
        self._attrs_dialog.show()

    def check_validity(self):
        self._field_name.check_validity()


class ScalarFieldWidget(BaseScalarFieldWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent, container)
        self._scalar_value = ScalarValueEdit(parent, container.module)
        self.layout().insertWidget(2, self._scalar_value)
        self._scalar_value.is_valid.connect(
            partial(self._validator.set_is_valid, self._scalar_value)
        )

    def check_validity(self):
        super().check_validity()
        self._scalar_value.check_validity()


class ScalarArrayFieldWidget(BaseScalarFieldWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent, container)
        self._scalar_array = ScalarArrayEdit(parent, container.module)
        self.layout().insertWidget(2, self._scalar_array)
        self._scalar_array.is_valid.connect(
            partial(self._validator.set_is_valid, self._scalar_array)
        )

    def check_validity(self):
        super().check_validity()
        self._scalar_array.check_validity()


class WriterModuleFieldWidget(BaseFieldWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent, container)
        if not isinstance(container.module, StreamModule):
            parent_node = container.module.parent_node
            new_module = F142Stream(
                parent_node=parent_node, source="", topic="", type="double"
            )
            parent_node.children[
                parent_node.children.index(container.module)
            ] = new_module
            container.module = new_module
        self._standard_settings = FileWriterModuleEdit(parent, container)
        self._standard_settings.sizeHintChanged.connect(self.sizeHintChanged.emit)
        self.layout().insertWidget(2, self._standard_settings)
        self._standard_settings.is_valid.connect(
            partial(self._validator.set_is_valid, self._standard_settings)
        )

    def check_validity(self):
        self._standard_settings.check_validity()

    sizeHintChanged = Signal()


class LinkModuleFieldWidget(BaseFieldWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent, container)
        if not isinstance(container.module, Link):
            parent_node = container.module.parent_node
            if isinstance(container.module, Dataset):
                new_module = Link(
                    parent_node=parent_node, name=container.module.name, target=""
                )
            else:
                new_module = Link(parent_node=parent_node, name="", target="")
            parent_node.children[
                parent_node.children.index(container.module)
            ] = new_module
            container.module = new_module
        self._link_settings = LinkEdit(parent, container)
        self.layout().addWidget(self._link_settings)
        self._link_settings.is_valid.connect(
            partial(self._validator.set_is_valid, self._link_settings)
        )

    def check_validity(self):
        self._link_settings.check_validity()


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
    def __init__(
        self,
        parent: QWidget,
        file_writer_module: FileWriterModule,
    ):
        super().__init__(parent)
        self._field_widget: Optional[QWidget] = None
        self._module_container = ModuleContainer(file_writer_module)
        self.field_type_combo: QComboBox = QComboBox()
        self.field_type_combo.addItems([item.value for item in FieldType])
        self.field_type_combo.setCurrentText(
            get_module_type(self._module_container.module).value
        )
        self.field_type_combo.currentIndexChanged.connect(self._field_type_changed)

        fix_horizontal_size = QSizePolicy()
        fix_horizontal_size.setHorizontalPolicy(QSizePolicy.Fixed)
        self.field_type_combo.setSizePolicy(fix_horizontal_size)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.field_type_combo)
        self.layout().setAlignment(Qt.AlignLeft)
        self.setFrameShadow(QFrame.Raised)
        self.setFrameShape(QFrame.StyledPanel)
        self._field_type_changed()

    def check_validity(self):
        if self._field_widget is not None:
            self._field_widget.check_validity()

    def _remove_existing_widget(self):
        if self._field_widget is not None:
            self._field_widget.hide()
            self._field_widget.is_valid.disconnect()
            self.layout().removeWidget(self._field_widget)
            self._field_widget = None

    def _instantiate_scalar_widgets(self):
        self._remove_existing_widget()
        self._field_widget = ScalarFieldWidget(self.parent(), self._module_container)
        self._field_widget.is_valid.connect(self.is_valid.emit)
        self.check_validity()
        self.layout().addWidget(self._field_widget)
        self.sizeHintChanged.emit()

    def _instantiate_array_widgets(self):
        self._remove_existing_widget()
        self._field_widget = ScalarArrayFieldWidget(
            self.parent(), self._module_container
        )
        self._field_widget.is_valid.connect(self.is_valid.emit)
        self.check_validity()
        self.layout().addWidget(self._field_widget)
        self.sizeHintChanged.emit()

    def _instantiate_stream_widgets(self):
        self._remove_existing_widget()
        self._field_widget = WriterModuleFieldWidget(
            self.parent(), self._module_container
        )
        self._field_widget.is_valid.connect(self.is_valid.emit)
        self._field_widget.sizeHintChanged.connect(self.sizeHintChanged.emit)
        self.check_validity()
        self.layout().addWidget(self._field_widget)
        self.sizeHintChanged.emit()

    def _instantiate_link_widgets(self):
        self._remove_existing_widget()
        self._field_widget = LinkModuleFieldWidget(
            self.parent(), self._module_container
        )
        self._field_widget.is_valid.connect(self.is_valid.emit)
        self.check_validity()
        self.layout().addWidget(self._field_widget)
        self.sizeHintChanged.emit()

    def _field_type_changed(self):
        populate_widget_map = {
            FieldType.scalar_dataset.value: self._instantiate_scalar_widgets,
            FieldType.array_dataset.value: self._instantiate_array_widgets,
            FieldType.kafka_stream.value: self._instantiate_stream_widgets,
            FieldType.link.value: self._instantiate_link_widgets,
        }

        populate_widget_map[self.field_type_combo.currentText()]()

    is_valid = Signal(bool)
    sizeHintChanged = Signal()


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
