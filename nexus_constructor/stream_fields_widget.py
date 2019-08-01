import uuid

import h5py
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLineEdit,
    QDialog,
    QLabel,
    QSpinBox,
)
import numpy as np

SCHEMAS = ["ev42", "f142", "hs00", "ns10"]
F142_TYPES = [
    "byte",
    "ubyte",
    "short",
    "ushort",
    "int",
    "uint",
    "long",
    "ulong",
    "float",
    "double",
    "string",
]


class StreamFieldsWidget(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setLayout(QGridLayout())
        self.setWindowModality(Qt.WindowModal)
        self.setModal(True)

        self.schema_label = QLabel("Schema: ")
        self.schema_combo = QComboBox()

        self.topic_label = QLabel("Topic: ")
        self.topic_line_edit = QLineEdit()
        self.topic_line_edit.setPlaceholderText("//broker[:port, default=9092]/topic")

        self.source_label = QLabel("Source: ")
        self.source_line_edit = QLineEdit()

        self.array_size_label = QLabel("Array size")
        self.array_size_spinbox = QSpinBox()
        self.array_size_spinbox.setMaximum(np.iinfo(np.int32).max)

        self.type_label = QLabel("Type: ")
        self.type_combo = QComboBox()
        self.type_combo.addItems(F142_TYPES)
        self.type_combo.currentTextChanged.connect(self._type_changed)

        self.schema_combo.currentTextChanged.connect(self.schema_type_changed)
        self.schema_combo.addItems(SCHEMAS)

        self.layout().addWidget(self.schema_label, 0, 0)
        self.layout().addWidget(self.schema_combo, 0, 1)

        self.layout().addWidget(self.topic_label, 1, 0)
        self.layout().addWidget(self.topic_line_edit, 1, 1)

        self.layout().addWidget(self.type_label, 2, 0)
        self.layout().addWidget(self.type_combo, 2, 1)

        self.layout().addWidget(self.array_size_label, 3, 0)
        self.layout().addWidget(self.array_size_spinbox, 3, 1)

        self.layout().addWidget(self.source_label, 4, 0)
        self.layout().addWidget(self.source_line_edit, 4, 1)

        self.schema_type_changed(self.schema_combo.currentText())
        self._type_changed(self.type_combo.currentText())

    def schema_type_changed(self, schema):
        self.parent().setWindowTitle(f"Editing {schema} stream field")
        if schema == "f142":
            self._set_edits_visible(True, True)
        elif schema == "ev42":
            self._set_edits_visible(False, False)
        elif schema == "hs00":
            self._set_edits_visible(True, False)
        elif schema == "ns10":
            self._set_edits_visible(True, False)

    def _set_edits_visible(self, source: bool, type: bool):
        self.source_label.setVisible(source)
        self.source_line_edit.setVisible(source)
        self.type_label.setVisible(type)
        self.type_combo.setVisible(type)

    def _type_changed(self, dtype):
        if self.type_combo.isVisible():
            is_double = dtype == "double"
            self.array_size_label.setVisible(is_double)
            self.array_size_spinbox.setVisible(is_double)
        else:
            self.array_size_label.setVisible(False)
            self.array_size_spinbox.setVisible(False)

    def get_stream_group(self):
        dtype = h5py.special_dtype(vlen=str)
        temp_file = h5py.File(
            name=str(uuid.uuid4()), driver="core", backing_store=False
        )
        group = temp_file.create_group("children")
        group.create_dataset(name="type", dtype=dtype, data="stream")
        stream_group = group.create_group("stream")
        stream_group.create_dataset(
            name="topic", dtype=dtype, data=self.topic_line_edit.text()
        )
        stream_group.create_dataset(
            name="writer_module", dtype=dtype, data=self.schema_combo.currentText()
        )
        return stream_group
