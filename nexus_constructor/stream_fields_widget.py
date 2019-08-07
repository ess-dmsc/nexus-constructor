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
    QPushButton,
    QGroupBox,
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

        self.hs00_unimplemented_label = QLabel(
            "hs00 (Event histograms) has not yet been fully implemented."
        )

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

        self.show_f142_advanced_options_button = QPushButton(
            text="Show/hide advanced options"
        )

        self.f142_advanced_group_box = QGroupBox(title="Advanced options for f142")
        self.show_f142_advanced_options_button.clicked.connect(
            self._show_advanced_options
        )
        self.f142_advanced_group_box.setLayout(QGridLayout())
        minimum_value = 0
        maximum_value = 100000000
        self.nexus_indices_index_every_mb_label = QLabel("nexus.indices.index_every_mb")
        self.nexus_indices_index_every_mb_spinbox = QSpinBox()
        self.nexus_indices_index_every_mb_spinbox.setRange(minimum_value, maximum_value)
        self.f142_advanced_group_box.layout().addWidget(
            self.nexus_indices_index_every_mb_label, 0, 0
        )
        self.f142_advanced_group_box.layout().addWidget(
            self.nexus_indices_index_every_mb_spinbox, 0, 1
        )

        self.nexus_chunk_mb_label = QLabel("nexus.indices.index_every_mb")
        self.nexus_chunk_mb_spinbox = QSpinBox()
        self.nexus_chunk_mb_spinbox.setRange(minimum_value, maximum_value)
        self.f142_advanced_group_box.layout().addWidget(self.nexus_chunk_mb_label, 1, 0)
        self.f142_advanced_group_box.layout().addWidget(
            self.nexus_chunk_mb_spinbox, 1, 1
        )

        self.nexus_buffer_size_label = QLabel("nexus.buffer.size_kb")
        self.nexus_buffer_size_spinbox = QSpinBox()
        self.nexus_buffer_size_spinbox.setRange(minimum_value, maximum_value)
        self.f142_advanced_group_box.layout().addWidget(
            self.nexus_buffer_size_label, 2, 0
        )
        self.f142_advanced_group_box.layout().addWidget(
            self.nexus_buffer_size_spinbox, 2, 1
        )

        self.nexus_packet_max_kb_label = QLabel("nexus.buffer.packet_max_kb")
        self.nexus_packet_max_kb_spinbox = QSpinBox()
        self.nexus_packet_max_kb_spinbox.setRange(minimum_value, maximum_value)
        self.f142_advanced_group_box.layout().addWidget(
            self.nexus_packet_max_kb_label, 3, 0
        )
        self.f142_advanced_group_box.layout().addWidget(
            self.nexus_packet_max_kb_spinbox, 3, 1
        )

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

        self.layout().addWidget(
            self.hs00_unimplemented_label, 5, 0, colspan=1, rowspan=2
        )

        # Spans both rows
        self.layout().addWidget(
            self.show_f142_advanced_options_button, 6, 0, colspan=1, rowspan=2
        )
        self.layout().addWidget(
            self.f142_advanced_group_box, 7, 0, colspan=1, rowspan=2
        )

        self.schema_type_changed(self.schema_combo.currentText())
        self._type_changed(self.type_combo.currentText())

    def _show_advanced_options(self):
        self.f142_advanced_group_box.setVisible(
            not self.f142_advanced_group_box.isVisible()
        )

    def schema_type_changed(self, schema: str):
        self.parent().setWindowTitle(f"Editing {schema} stream field")
        self.hs00_unimplemented_label.setVisible(False)
        self.f142_advanced_group_box.setVisible(False)
        self.show_f142_advanced_options_button.setVisible(False)
        if schema == "f142":
            self._set_edits_visible(True, True)
            self.show_f142_advanced_options_button.setVisible(True)
            self.f142_advanced_group_box.setVisible(False)
        elif schema == "ev42":
            self._set_edits_visible(False, False)
        elif schema == "hs00":
            self._set_edits_visible(True, False)
            self.hs00_unimplemented_label.setVisible(True)

        elif schema == "ns10":
            self._set_edits_visible(True, False, "nicos/<device>/<parameter>")

    def _set_edits_visible(self, source: bool, type: bool, source_hint=None):
        self.source_label.setVisible(source)
        self.source_line_edit.setVisible(source)
        self.type_label.setVisible(type)
        self.type_combo.setVisible(type)
        if source_hint:
            self.source_line_edit.setPlaceholderText(source_hint)
        else:
            self.source_line_edit.setPlaceholderText("")

    def _type_changed(self, dtype: str):
        if self.type_combo.isVisible():
            is_double = dtype == "double"
            self.array_size_label.setVisible(is_double)
            self.array_size_spinbox.setVisible(is_double)
        else:
            self.array_size_label.setVisible(False)
            self.array_size_spinbox.setVisible(False)

    def get_stream_group(self) -> h5py.Group:
        string_dtype = h5py.special_dtype(vlen=str)
        temp_file = h5py.File(
            name=str(uuid.uuid4()), driver="core", backing_store=False
        )
        group = temp_file.create_group("children")
        group.create_dataset(name="type", dtype=string_dtype, data="stream")
        stream_group = group.create_group("stream")
        stream_group.create_dataset(
            name="topic", dtype=string_dtype, data=self.topic_line_edit.text()
        )
        stream_group.create_dataset(
            name="writer_module",
            dtype=string_dtype,
            data=self.schema_combo.currentText(),
        )

        schema = self.schema_combo.currentText()

        if schema == "f142":
            stream_group.create_dataset(
                "type", dtype=string_dtype, data=self.type_combo.currentText()
            )
            if self.type_combo.currentText() == "double":
                stream_group.create_dataset(
                    "array_size", data=self.array_size_spinbox.value()
                )
        if schema != "ev42":
            stream_group.create_dataset(
                "source", dtype=string_dtype, data=self.source_line_edit.text()
            )
        return stream_group
