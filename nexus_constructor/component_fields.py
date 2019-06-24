from PySide2.QtWidgets import QPushButton, QHBoxLayout, QFrame, QComboBox, QDialog
from PySide2.QtWidgets import QCompleter, QLineEdit, QSizePolicy
from PySide2.QtCore import QStringListModel, Qt
from typing import List
from nexus_constructor.field_type import DatasetType, FieldType

_field_types = {}


class FieldNameLineEdit(QLineEdit):
    def __init__(self, possible_field_names: List[str]):
        super().__init__()
        self.setCompleter(QCompleter())
        model = QStringListModel()
        model.setStringList(possible_field_names)
        self.completer().setModel(model)
        self.setPlaceholderText("Enter name of new field")
        self.setMinimumWidth(200)
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


class FieldWidget(QFrame):
    def __init__(self, possible_field_names: List[str], parent=None):
        super(FieldWidget, self).__init__(parent)

        self.field_name_edit = FieldNameLineEdit(possible_field_names)

        self.field_type_combo = QComboBox()
        self.field_type_combo.addItems([item.value for item in FieldType])
        self.field_type_combo.currentIndexChanged.connect(self.field_type_changed)
        self.field_type_combo.setMinimumWidth(100)
        fix_horizontal_size = QSizePolicy()
        fix_horizontal_size.setHorizontalPolicy(QSizePolicy.Fixed)
        self.field_type_combo.setSizePolicy(fix_horizontal_size)

        self.value_line_edit = QLineEdit()
        self.nx_class_combo = QComboBox()

        self.edit_button = QPushButton("Edit")
        edit_button_size = 50
        self.edit_button.setMinimumWidth(edit_button_size)
        self.edit_button.setMaximumWidth(edit_button_size)
        self.edit_button.setSizePolicy(fix_horizontal_size)
        self.edit_button.clicked.connect(self.show_edit_dialog)

        self.value_type_combo = QComboBox()
        self.value_type_combo.addItems([item.value for item in DatasetType])

        # TODO: actually remove stuff - use signal to listview?
        # TODO: set up nx classes
        self.remove_button = QPushButton("Remove")

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.field_name_edit)
        self.layout.addWidget(self.field_type_combo)
        self.layout.addWidget(self.value_line_edit)
        self.layout.addWidget(self.nx_class_combo)
        self.layout.addWidget(self.edit_button)
        self.layout.addWidget(self.value_type_combo)
        self.layout.addWidget(self.remove_button)

        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)

        self.setFrameShadow(QFrame.Raised)
        self.setFrameShape(QFrame.StyledPanel)

        # Set the layout for the default field type
        self.field_type_changed()

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
        self.edit_dialog = QDialog()
        self.edit_dialog.show()
        if self.field_type_combo.currentText() == FieldType.scalar_dataset.value:
            # TODO: show scalar edit panel
            pass
        elif self.field_type_combo.currentText() == FieldType.array_dataset.value:
            # TODO: show array edit panel
            pass
        elif self.field_type_combo.currentText() == FieldType.kafka_stream.value:
            # TODO: show kafka stream panel
            pass
        elif self.field_type_combo.currentText() == FieldType.link.value:
            # TODO: show link panel
            pass
        elif self.field_type_combo.currentText() == FieldType.nx_class.value:
            # TODO: show nx class panels
            pass
