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

    is_valid = Signal(bool)


class BaseScalarFieldWidget(BaseFieldWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent, container)
        if not isinstance(container.module, Dataset):
            parent_node = container.module.parent_node
            new_module = Dataset(parent_node=parent_node, name="", values=0)
            parent_node.children[parent_node.children.index(container.module)] = new_module
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
        self._validator.is_valid.connect(self.is_valid.emit)

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
            new_module = F142Stream(parent_node=parent_node, source="", topic="", type="double")
            parent_node.children[parent_node.children.index(container.module)] = new_module
            container.module = new_module
        self._standard_settings = FileWriterModuleEdit(parent, container)
        self.layout().insertWidget(2, self._standard_settings)
        self._standard_settings.is_valid.connect(partial(self._validator.set_is_valid, self._standard_settings))

    def check_validity(self):
        self._standard_settings.check_validity()


class LinkModuleFieldWidget(BaseFieldWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent, container)
        if not isinstance(container.module, Link):
            parent_node = container.module.parent_node
            if isinstance(container.module, Dataset):
                new_module = Link(parent_node=parent_node, name=container.module.name, target="")
            else:
                new_module = Link(parent_node=parent_node, name="", target="")
            parent_node.children[parent_node.children.index(container.module)] = new_module
            container.module = new_module
        self._link_settings = LinkEdit(parent, container)
        self.layout().addWidget(self._link_settings)
        self._link_settings.is_valid.connect(partial(self._validator.set_is_valid, self._link_settings))

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
        self._module_container = ModuleContainer(file_writer_module)

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
        self.field_type_combo: QComboBox = QComboBox()
        self.field_type_combo.addItems([item.value for item in FieldType])
        self.field_type_combo.setCurrentText(
            get_module_type(self._module_container.module).value
        )
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

    def _instantiate_array_widgets(self):
        self._remove_existing_widget()
        self._field_widget = ScalarArrayFieldWidget(self.parent(), self._module_container)
        self._field_widget.is_valid.connect(self.is_valid.emit)
        self.check_validity()
        self.layout().addWidget(self._field_widget)

    def _instantiate_stream_widgets(self):
        self._remove_existing_widget()
        self._field_widget = WriterModuleFieldWidget(self.parent(), self._module_container)
        self._field_widget.is_valid.connect(self.is_valid.emit)
        self.check_validity()
        self.layout().addWidget(self._field_widget)

    def _instantiate_link_widgets(self):
        self._remove_existing_widget()
        self._field_widget = LinkModuleFieldWidget(self.parent(), self._module_container)
        self._field_widget.is_valid.connect(self.is_valid.emit)
        self.check_validity()
        self.layout().addWidget(self._field_widget)

    def _field_type_changed(self):
        populate_widget_map = {
            FieldType.scalar_dataset.value: self._instantiate_scalar_widgets,
            FieldType.array_dataset.value: self._instantiate_array_widgets,
            FieldType.kafka_stream.value: self._instantiate_stream_widgets,
            FieldType.link.value: self._instantiate_link_widgets,
        }

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
    is_valid = Signal(bool)


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
