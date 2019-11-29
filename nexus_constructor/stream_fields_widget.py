import uuid
from functools import partial
from typing import List, ItemsView

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
    QRadioButton,
    QCheckBox,
    QFormLayout,
)
import numpy as np

SCHEMAS = ["ev42", "f142", "hs00", "ns10", "TdcTime", "senv"]
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

STRING_DTYPE = h5py.special_dtype(vlen=str)

NEXUS_INDICES_INDEX_EVERY_MB = "nexus.indices.index_every_mb"
NEXUS_INDICES_INDEX_EVERY_KB = "nexus.indices.index_every_kb"
STORE_LATEST_INTO = "store_latest_into"
NEXUS_CHUNK_CHUNK_MB = "nexus.chunk.chunk_mb"
NEXUS_CHUNK_CHUNK_KB = "nexus.chunk.chunk_kb"
ADC_PULSE_DEBUG = "adc_pulse_debug"


def check_if_advanced_options_should_be_enabled(
    elements: List[str], field: h5py.Group
) -> bool:
    """
    Checks whether the advanced options box should be enabled by checking if any of the advanced options have existing values.
    :param elements: list of names to check if exist
    :param field: the field group
    """
    return any(item in field.keys() for item in elements)


def fill_in_advanced_options(elements: ItemsView[str, QSpinBox], field: h5py.Group):
    for nxs_string, spinner in elements:
        if nxs_string in field.keys():
            spinner.setValue(field[nxs_string][()])


class StreamFieldsWidget(QDialog):
    """
    A stream widget containing schema-specific properties.
    """

    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setLayout(QGridLayout())
        self.setWindowModality(Qt.WindowModal)
        self.setModal(True)
        self.minimum_spinbox_value = 0
        self.maximum_spinbox_value = 100000000

        self.hs00_unimplemented_label = QLabel(
            "hs00 (Event histograms) has not yet been fully implemented."
        )

        self.schema_label = QLabel("Schema: ")
        self.schema_combo = QComboBox()

        self.topic_label = QLabel("Topic: ")
        self.topic_line_edit = QLineEdit()

        self.source_label = QLabel("Source: ")
        self.source_line_edit = QLineEdit()

        self.array_size_label = QLabel("Array size")
        self.array_size_spinbox = QSpinBox()
        self.array_size_spinbox.setMaximum(np.iinfo(np.int32).max)

        self.type_label = QLabel("Type: ")
        self.type_combo = QComboBox()
        self.type_combo.addItems(F142_TYPES)

        self.show_advanced_options_button = QPushButton(
            text="Show/hide advanced options"
        )
        self.show_advanced_options_button.setCheckable(True)
        self.show_advanced_options_button.clicked.connect(self._show_advanced_options)

        self._set_up_f142_group_box()
        self._set_up_ev42_group_box()

        self.scalar_radio = QRadioButton(text="Scalar")
        self.scalar_radio.clicked.connect(partial(self._show_array_size, False))
        self.scalar_radio.setChecked(True)
        self.scalar_radio.clicked.emit()

        self.array_radio = QRadioButton(text="Array")
        self.array_radio.clicked.connect(partial(self._show_array_size, True))

        self.schema_combo.currentTextChanged.connect(self._schema_type_changed)
        self.schema_combo.addItems(SCHEMAS)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.parent().close)

        self.set_advanced_options_state()

        self.layout().addWidget(self.schema_label, 0, 0)
        self.layout().addWidget(self.schema_combo, 0, 1)

        self.layout().addWidget(self.topic_label, 1, 0)
        self.layout().addWidget(self.topic_line_edit, 1, 1)

        self.layout().addWidget(self.source_label, 2, 0)
        self.layout().addWidget(self.source_line_edit, 2, 1)

        self.layout().addWidget(self.type_label, 3, 0)
        self.layout().addWidget(self.type_combo, 3, 1)

        self.layout().addWidget(self.scalar_radio, 4, 0)
        self.layout().addWidget(self.array_radio, 4, 1)

        self.layout().addWidget(self.array_size_label, 5, 0)
        self.layout().addWidget(self.array_size_spinbox, 5, 1)

        self.layout().addWidget(self.hs00_unimplemented_label, 6, 0, 1, 2)

        # Spans both rows
        self.layout().addWidget(self.show_advanced_options_button, 7, 0, 1, 2)
        self.layout().addWidget(self.f142_advanced_group_box, 8, 0, 1, 2)

        self.layout().addWidget(self.ev42_advanced_group_box, 9, 0, 1, 2)

        self.layout().addWidget(self.ok_button, 10, 0, 1, 2)

        self._schema_type_changed(self.schema_combo.currentText())

    def _set_up_ev42_group_box(self):
        """
        Sets up the UI for ev42 advanced options.
        """
        self.ev42_nexus_elements = [
            NEXUS_INDICES_INDEX_EVERY_MB,
            NEXUS_INDICES_INDEX_EVERY_KB,
            NEXUS_CHUNK_CHUNK_MB,
            NEXUS_CHUNK_CHUNK_KB,
        ]

        self.ev42_nexus_to_spinner_ui_element = {}

        self.ev42_advanced_group_box = QGroupBox(
            parent=self.show_advanced_options_button
        )
        self.ev42_advanced_group_box.setLayout(QFormLayout())

        self.ev42_adc_pulse_debug_label = QLabel(ADC_PULSE_DEBUG)
        self.ev42_adc_pulse_debug_checkbox = QCheckBox()

        self.ev42_advanced_group_box.layout().addRow(
            self.ev42_adc_pulse_debug_label, self.ev42_adc_pulse_debug_checkbox
        )

        self.add_labels_and_spinboxes_for_advanced_options(
            self.ev42_nexus_elements,
            self.ev42_advanced_group_box,
            self.ev42_nexus_to_spinner_ui_element,
        )

    def add_labels_and_spinboxes_for_advanced_options(
        self, elements, group_box, nexus_to_spinner
    ):
        for nexus_string in elements:
            label = QLabel(nexus_string)
            spinner = QSpinBox()
            spinner.setRange(self.minimum_spinbox_value, self.maximum_spinbox_value)

            group_box.layout().addRow(label, spinner)

            nexus_to_spinner[nexus_string] = spinner

    def _set_up_f142_group_box(self):
        """
        Sets up the UI for the f142 advanced options.
        """
        self.f142_advanced_group_box = QGroupBox(
            parent=self.show_advanced_options_button
        )
        self.f142_advanced_group_box.setLayout(QFormLayout())
        self.f142_nexus_to_spinner_ui_element = {}

        self.f142_nexus_elements = [
            NEXUS_INDICES_INDEX_EVERY_MB,
            NEXUS_INDICES_INDEX_EVERY_KB,
            STORE_LATEST_INTO,
        ]

        self.add_labels_and_spinboxes_for_advanced_options(
            self.f142_nexus_elements,
            self.f142_advanced_group_box,
            self.f142_nexus_to_spinner_ui_element,
        )

    def _show_advanced_options(self):
        schema = self.schema_combo.currentText()
        if schema == "f142":
            self.f142_advanced_group_box.setVisible(
                not self.f142_advanced_group_box.isVisible()
            )
        elif schema == "ev42":
            self.ev42_advanced_group_box.setVisible(
                not self.ev42_advanced_group_box.isVisible()
            )

        self.set_advanced_options_state()

    def set_advanced_options_state(self):
        """Used for getting the stream options when the dialog is closed."""
        self.advanced_options_enabled = (
            self.ev42_advanced_group_box.isVisible()
            or self.f142_advanced_group_box.isVisible()
        )

    def _show_array_size(self, show: bool):
        self.array_size_spinbox.setVisible(show)
        self.array_size_label.setVisible(show)

    def _schema_type_changed(self, schema: str):
        self.parent().setWindowTitle(f"Editing {schema} stream field")
        self.hs00_unimplemented_label.setVisible(False)
        self.f142_advanced_group_box.setVisible(False)
        self.ev42_advanced_group_box.setVisible(False)
        self.show_advanced_options_button.setVisible(False)
        self.show_advanced_options_button.setChecked(False)
        self.set_advanced_options_state()
        if schema == "f142":
            self._set_edits_visible(True, True)
            self.show_advanced_options_button.setVisible(True)
            self.f142_advanced_group_box.setVisible(False)
        elif schema == "ev42":
            self._set_edits_visible(True, False)
            self.show_advanced_options_button.setVisible(True)
            self.ev42_advanced_group_box.setVisible(False)
        elif schema == "hs00":
            self._set_edits_visible(True, False)
            self.hs00_unimplemented_label.setVisible(True)
        elif schema == "ns10":
            self._set_edits_visible(True, False, "nicos/<device>/<parameter>")
        elif schema == "TdcTime" or schema == "senv":
            self._set_edits_visible(True, False)

    def _set_edits_visible(self, source: bool, type: bool, source_hint=None):
        self.source_label.setVisible(source)
        self.source_line_edit.setVisible(source)
        self.type_label.setVisible(type)
        self.type_combo.setVisible(type)
        self.array_radio.setVisible(type)
        self.scalar_radio.setVisible(type)
        if source_hint:
            self.source_line_edit.setPlaceholderText(source_hint)
        else:
            self.source_line_edit.setPlaceholderText("")

    def get_stream_group(self) -> h5py.Group:
        """
        Create the stream group with a temporary in-memory HDF5 file.
        :return: The created HDF group.
        """

        temp_file = h5py.File(
            name=str(uuid.uuid4()), driver="core", backing_store=False, mode="x"
        )
        group = temp_file.create_group("children")
        group.create_dataset(name="type", dtype=STRING_DTYPE, data="stream")
        stream_group = group.create_group(self.parent().parent().field_name_edit.text())
        stream_group.attrs["NX_class"] = "NCstream"
        stream_group.create_dataset(
            name="topic", dtype=STRING_DTYPE, data=self.topic_line_edit.text()
        )
        stream_group.create_dataset(
            name="writer_module",
            dtype=STRING_DTYPE,
            data=self.schema_combo.currentText(),
        )

        schema = self.schema_combo.currentText()
        stream_group.create_dataset(
            "source", dtype=STRING_DTYPE, data=self.source_line_edit.text()
        )
        if schema == "f142":
            self._create_f142_fields(stream_group)

        elif schema == "ev42":
            self._create_ev42_fields(stream_group)
        return stream_group

    def _create_ev42_fields(self, stream_group: h5py.Group):
        """
        Create ev42 fields in the given group if advanced options are specified.
        :param stream_group: The group to apply fields to.
        """
        if self.advanced_options_enabled:
            if self.ev42_adc_pulse_debug_checkbox.isChecked():
                stream_group.create_dataset(
                    ADC_PULSE_DEBUG,
                    dtype=bool,
                    data=self.ev42_adc_pulse_debug_checkbox.isChecked(),
                )

            for (
                nexus_string,
                ui_element,
            ) in self.ev42_nexus_to_spinner_ui_element.items():
                if ui_element.value() > 0:
                    stream_group.create_dataset(
                        nexus_string, dtype=int, data=ui_element.value()
                    )

    def _create_f142_fields(self, stream_group: h5py.Group):
        """
        Create f142 fields in the given group if advanced options are specified.
        :param stream_group: The group to apply fields to.
        """
        stream_group.create_dataset(
            "type", dtype=STRING_DTYPE, data=self.type_combo.currentText()
        )
        if self.array_radio.isChecked():
            stream_group.create_dataset(
                "array_size", data=self.array_size_spinbox.value()
            )
        if self.advanced_options_enabled:
            # Use strings for names, we don't care if it's byte-encoded as it will output to JSON anyway.
            for (
                nexus_string,
                ui_element,
            ) in self.f142_nexus_to_spinner_ui_element.items():
                if ui_element.value() > 0:
                    stream_group.create_dataset(
                        nexus_string, dtype=int, data=ui_element.value()
                    )

    def fill_in_existing_ev42_fields(self, field: h5py.Group):
        """
        Fill in specific existing ev42 fields into the new UI field.
        :param field: The stream group
        :param new_ui_field: The new UI field to be filled in
        """
        all_ev42_elements = list(self.ev42_nexus_elements)
        all_ev42_elements.append(ADC_PULSE_DEBUG)

        advanced_options = check_if_advanced_options_should_be_enabled(
            all_ev42_elements, field
        )

        if advanced_options:
            self.ev42_advanced_group_box.setEnabled(True)
            self.set_advanced_options_state()

        if ADC_PULSE_DEBUG in field.keys():
            self.ev42_adc_pulse_debug_checkbox.setChecked(
                bool(field[ADC_PULSE_DEBUG][()])
            )

        fill_in_advanced_options(self.ev42_nexus_to_spinner_ui_element.items(), field)

    def fill_in_existing_f142_fields(self, field: h5py.Group):
        """
        Fill in specific existing f142 fields into the new UI field.
        :param field: The stream group
        :param new_ui_field: The new UI field to be filled in
        """
        self.type_combo.setCurrentText(field["type"][()])
        if "array_size" in field.keys():
            self.array_radio.setChecked(True)
            self.scalar_radio.setChecked(False)
            self.array_size_spinbox.setValue(field["array_size"][()])
        else:
            self.array_radio.setChecked(False)
            self.scalar_radio.setChecked(True)

        advanced_options = check_if_advanced_options_should_be_enabled(
            self.f142_nexus_elements, field
        )

        if advanced_options:
            self.f142_advanced_group_box.setEnabled(True)
            self.set_advanced_options_state()

        fill_in_advanced_options(self.f142_nexus_to_spinner_ui_element.items(), field)

    def update_existing_stream_info(self, field: h5py.Group):
        """
        Fill in stream fields and properties into the new UI field.
        :param field: The stream group
        :param new_ui_field: The new UI field to be filled in
        """
        schema = field["writer_module"][()]
        self.schema_combo.setCurrentText(str(schema))
        self.topic_line_edit.setText(str(field["topic"][()]))
        self.source_line_edit.setText(str(field["source"][()]))
        if schema == "f142":
            self.fill_in_existing_f142_fields(field)
        if schema == "ev42":
            self.fill_in_existing_ev42_fields(field)
