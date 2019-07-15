from functools import partial
from PySide2.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QFrame,
    QComboBox,
    QDialog,
    QListWidget,
    QMessageBox,
    QGridLayout,
)
from PySide2.QtWidgets import QCompleter, QLineEdit, QSizePolicy
from PySide2.QtCore import QStringListModel, Qt, Signal, QEvent, QObject
from typing import List
from nexus_constructor.component import Component
import numpy as np

from nexus_constructor.table_widget import TableWidget
from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import (
    FieldValueValidator,
    FieldType,
    DATASET_TYPE,
    NameValidator,
)


class FieldNameLineEdit(QLineEdit):
    def __init__(self, possible_field_names: List[str]):
        super().__init__()
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

    def __init__(self, possible_field_names: List[str], parent: QListWidget = None):
        super(FieldWidget, self).__init__(parent)

        self.edit_dialog = QDialog()
        self.table_view = TableWidget()
        self.field_name_edit = FieldNameLineEdit(possible_field_names)

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
        self.value_line_edit.setValidator(
            FieldValueValidator(self.field_type_combo, self.value_type_combo)
        )
        self.value_line_edit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self.value_line_edit,
                tooltip_on_accept="Value is cast-able to numpy type.",
                tooltip_on_reject="Value is not cast-able to selected numpy type.",
            )
        )
        self.dataset_type_changed(0)

        self.nx_class_combo = QComboBox()

        self.edit_button = QPushButton("Edit")
        edit_button_size = 50
        self.edit_button.setMinimumWidth(edit_button_size)
        self.edit_button.setMaximumWidth(edit_button_size)
        self.edit_button.setSizePolicy(fix_horizontal_size)
        self.edit_button.clicked.connect(self.show_edit_dialog)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.field_name_edit)
        self.layout.addWidget(self.field_type_combo)
        self.layout.addWidget(self.value_line_edit)
        self.layout.addWidget(self.nx_class_combo)
        self.layout.addWidget(self.edit_button)
        self.layout.addWidget(self.value_type_combo)

        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)

        self.setFrameShadow(QFrame.Raised)
        self.setFrameShape(QFrame.StyledPanel)

        # Allow selecting this field widget in a list by clicking on it's contents
        self.field_name_edit.installEventFilter(self)

        self._set_up_name_validator(parent)
        self.field_name_edit.validator().is_valid.emit(False)

        self.value_line_edit.installEventFilter(self)
        self.nx_class_combo.installEventFilter(self)

        # These cause odd double-clicking behaviour when using an event filter so just connecting to the clicked() signals instead.
        self.edit_button.clicked.connect(self.something_clicked)
        self.value_type_combo.highlighted.connect(self.something_clicked)
        self.field_type_combo.highlighted.connect(self.something_clicked)

        # Set the layout for the default field type
        self.field_type_changed()

    def _set_up_name_validator(self, parent):
        field_widgets = []
        for i in range(parent.count()):
            field_widgets.append(parent.itemWidget(parent.item(i)))
        self.field_name_edit.setValidator(NameValidator(field_widgets))
        self.field_name_edit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self.field_name_edit,
                tooltip_on_accept="Field name is valid.",
                tooltip_on_reject=f"Field name is not valid",
            )
        )

    @property
    def field_type(self):
        return FieldType(self.field_type_combo.currentText())

    @property
    def name(self):
        return self.field_name_edit.text()

    @property
    def dtype(self):
        if self.field_type == FieldType.scalar_dataset:
            return self.value.dtype
        if self.field_type == FieldType.array_dataset:
            return self.table_view.model.array.dtype

    @property
    def value(self):
        if self.field_type == FieldType.scalar_dataset:
            return DATASET_TYPE[self.value_type_combo.currentText()](
                self.value_line_edit.text()
            )
        elif self.field_type == FieldType.array_dataset:
            return self.table_view.model.array

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.MouseButtonPress:
            self.something_clicked.emit()
            return True
        else:
            return False

    def field_type_changed(self):
        if self.field_type_combo.currentText() == FieldType.scalar_dataset.value:
            self.set_visibility(True, False, False, True)
        elif self.field_type_combo.currentText() == FieldType.array_dataset.value:
            self.set_visibility(False, False, True, True)
        elif self.field_type_combo.currentText() == FieldType.kafka_stream.value:
            self.set_visibility(False, False, True, False)
        elif self.field_type_combo.currentText() == FieldType.link.value:
            self.set_visibility(True, False, False, False)
        elif self.field_type_combo.currentText() == FieldType.nx_class.value:
            self.set_visibility(False, True, False, False)

    def set_visibility(
        self,
        show_value_line_edit,
        show_nx_class_combo,
        show_edit_button,
        show_value_type_combo,
    ):
        self.value_line_edit.setVisible(show_value_line_edit)
        self.nx_class_combo.setVisible(show_nx_class_combo)
        self.edit_button.setVisible(show_edit_button)
        self.value_type_combo.setVisible(show_value_type_combo)

    def show_edit_dialog(self):
        if self.field_type_combo.currentText() == FieldType.array_dataset.value:
            self.edit_dialog.setLayout(QGridLayout())
            self.edit_dialog.layout().addWidget(self.table_view)
        elif self.field_type_combo.currentText() == FieldType.kafka_stream.value:
            # TODO: show kafka stream panel
            pass
        elif self.field_type_combo.currentText() == FieldType.nx_class.value:
            # TODO: show nx class panels
            pass
        self.edit_dialog.show()


def add_fields_to_component(component: Component, fields_widget: QListWidget):
    """
    Adds fields from a list widget to a component.
    :param component: Component to add the field to.
    :param fields_widget: The field list widget to extract field information such the name and value of each field.
    """
    for i in range(fields_widget.count()):
        widget = fields_widget.itemWidget(fields_widget.item(i))
        try:
            component.set_field(widget.name, widget.value, widget.dtype)
        except ValueError:
            dialog = QMessageBox(
                icon=QMessageBox.Warning,
                text=f"Warning: field {widget.name} not added",
                parent=fields_widget.parent().parent(),
            )
            dialog.setWindowTitle("Field invalid")
            dialog.show()
