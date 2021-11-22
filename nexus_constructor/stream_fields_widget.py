from functools import partial

import numpy as np
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
)

from nexus_constructor.common_attrs import ARRAY, SCALAR
from nexus_constructor.model.group import Group
from nexus_constructor.model.module import (
    ADC_PULSE_DEBUG,
    CHUNK_SIZE,
    CUE_INTERVAL,
    EV42Stream,
    F142Stream,
    HS00Stream,
    NS10Stream,
    SENVStream,
    StreamModule,
    TDCTStream,
    WriterModules,
)

# TODO: CHECKS NEED TO BE IMPLEMENTED FOR NEW FIELDS IN STREAM ACCORDING TO
# TODO: FILE WRITER DOCUMENTATION.

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


def check_if_advanced_options_should_be_enabled(advanced_fields) -> bool:
    """
    Checks whether the advanced options box should be enabled by checking if any of the advanced options have existing values.
    :param advanced_fields: the field group
    """
    return any(item is not None for item in advanced_fields)


class StreamFieldsWidget(QDialog):
    """
    A stream widget containing schema-specific properties.
    """

    def __init__(self, parent, show_only_f142_stream: bool = False):
        super().__init__()
        self.setParent(parent)
        self.setLayout(QGridLayout())
        self.setWindowModality(Qt.WindowModal)
        self.setModal(True)

        self._show_only_f142_stream = show_only_f142_stream
        self.minimum_spinbox_value = 0
        self.maximum_spinbox_value = 100_000_000
        self.advanced_options_enabled = False

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
        self.type_combo.setCurrentText("double")

        self.value_units_edit = QLineEdit()
        self.value_units_label = QLabel("Value Units:")

        self.show_advanced_options_button = QPushButton(
            text="Show/hide advanced options"
        )
        self.show_advanced_options_button.setCheckable(True)
        self.show_advanced_options_button.clicked.connect(
            self.advanced_options_button_clicked
        )

        self._set_up_f142_group_box()
        self._set_up_ev42_group_box()

        self.scalar_radio = QRadioButton(text=SCALAR)
        self.scalar_radio.clicked.connect(partial(self._show_array_size, False))
        self.scalar_radio.setChecked(True)
        self.scalar_radio.clicked.emit()

        self.array_radio = QRadioButton(text=ARRAY)
        self.array_radio.clicked.connect(partial(self._show_array_size, True))

        self.schema_combo.currentTextChanged.connect(self._schema_type_changed)
        if self._show_only_f142_stream:
            self.schema_combo.addItems([WriterModules.F142.value])
        else:
            self.schema_combo.addItems([e.value for e in WriterModules])

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.parent().close)

        self.layout().addWidget(self.schema_label, 0, 0)
        self.layout().addWidget(self.schema_combo, 0, 1)

        self.layout().addWidget(self.topic_label, 1, 0)
        self.layout().addWidget(self.topic_line_edit, 1, 1)

        self.layout().addWidget(self.source_label, 2, 0)
        self.layout().addWidget(self.source_line_edit, 2, 1)

        self.layout().addWidget(self.value_units_label, 3, 0)
        self.layout().addWidget(self.value_units_edit, 3, 1)
        self.value_units_label.setVisible(False)
        self.value_units_edit.setVisible(False)

        self.layout().addWidget(self.type_label, 4, 0)
        self.layout().addWidget(self.type_combo, 4, 1)

        self.layout().addWidget(self.scalar_radio, 5, 0)
        self.layout().addWidget(self.array_radio, 5, 1)

        self.layout().addWidget(self.array_size_label, 6, 0)
        self.layout().addWidget(self.array_size_spinbox, 6, 1)

        self.layout().addWidget(self.hs00_unimplemented_label, 7, 0, 1, 2)

        # Spans both rows
        self.layout().addWidget(self.show_advanced_options_button, 8, 0, 1, 2)
        self.layout().addWidget(self.f142_advanced_group_box, 9, 0, 1, 2)

        self.layout().addWidget(self.ev42_advanced_group_box, 10, 0, 1, 2)

        self.layout().addWidget(self.ok_button, 11, 0, 1, 2)

        self._schema_type_changed(self.schema_combo.currentText())

    def advanced_options_button_clicked(self):
        self._show_advanced_options(show=self.show_advanced_options_button.isChecked())

    def _set_up_ev42_group_box(self):
        """
        Sets up the UI for ev42 advanced options.
        """
        self.ev42_advanced_group_box = QGroupBox(
            parent=self.show_advanced_options_button
        )
        self.ev42_advanced_group_box.setLayout(QFormLayout())

        self.ev42_adc_pulse_debug_label = QLabel(ADC_PULSE_DEBUG)
        self.ev42_adc_pulse_debug_checkbox = QCheckBox()
        self.ev42_advanced_group_box.layout().addRow(
            self.ev42_adc_pulse_debug_label, self.ev42_adc_pulse_debug_checkbox
        )

        self.ev42_index_every_mb_spinner = (
            self.create_label_and_spinbox_for_advanced_option(
                CHUNK_SIZE, self.ev42_advanced_group_box
            )
        )
        self.ev42_index_every_kb_spinner = (
            self.create_label_and_spinbox_for_advanced_option(
                CUE_INTERVAL, self.ev42_advanced_group_box
            )
        )

    def create_label_and_spinbox_for_advanced_option(
        self, nexus_string: str, group_box: QGroupBox
    ):
        """
        Creates a SpinBox with a label and adds them to GroupBox then returns the SpinBox.
        :param nexus_string: The nexus string label for the SpinBox.
        :param group_box: The GroupBox that the label and SpinBox should be added to.
        :return: The newly created SpinBox.
        """
        label = QLabel(nexus_string)
        spinner = QSpinBox()
        spinner.setRange(self.minimum_spinbox_value, self.maximum_spinbox_value)
        group_box.layout().addRow(label, spinner)

        return spinner

    def _set_up_f142_group_box(self):
        """
        Sets up the UI for the f142 advanced options.
        """
        self.f142_advanced_group_box = QGroupBox(
            parent=self.show_advanced_options_button
        )
        self.f142_advanced_group_box.setLayout(QFormLayout())

        self.f142_index_every_mb_spinner = (
            self.create_label_and_spinbox_for_advanced_option(
                CHUNK_SIZE, self.f142_advanced_group_box
            )
        )
        self.f142_index_every_kb_spinner = (
            self.create_label_and_spinbox_for_advanced_option(
                CUE_INTERVAL, self.f142_advanced_group_box
            )
        )

    def _show_advanced_options(self, show):
        schema = self.schema_combo.currentText()
        if schema == WriterModules.F142.value:
            self.f142_advanced_group_box.setVisible(show)
        elif schema == WriterModules.EV42.value:
            self.ev42_advanced_group_box.setVisible(show)
        self.advanced_options_enabled = show

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
        self.value_units_label.setVisible(False)
        self.value_units_edit.setVisible(False)
        if schema == WriterModules.F142.value:
            self.value_units_label.setVisible(True)
            self.value_units_edit.setVisible(True)
            self._set_edits_visible(True, True)
            self.show_advanced_options_button.setVisible(True)
            self.f142_advanced_group_box.setVisible(False)
        elif schema == WriterModules.EV42.value:
            self._set_edits_visible(True, False)
            self.show_advanced_options_button.setVisible(True)
            self.ev42_advanced_group_box.setVisible(False)
        elif schema == WriterModules.HS00.value:
            self._set_edits_visible(True, False)
            self.hs00_unimplemented_label.setVisible(True)
        elif schema == WriterModules.NS10.value:
            self._set_edits_visible(True, False, "nicos/<device>/<parameter>")
        elif (
            schema == WriterModules.TDCTIME.value or schema == WriterModules.SENV.value
        ):
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

    def get_stream_group(self) -> Group:
        """
        Create the stream group
        :return: The created StreamGroup
        """

        source = self.source_line_edit.text()
        topic = self.topic_line_edit.text()
        stream: StreamModule = None
        type = self.type_combo.currentText()
        current_schema = self.schema_combo.currentText()
        group_name = self.parent().parent().field_name_edit.text()
        stream_group = Group(group_name)
        if current_schema == WriterModules.F142.value:
            value_units = self.value_units_edit.text()
            array_size = self.array_size_spinbox.value()
            stream = F142Stream(
                parent_node=stream_group,
                source=source,
                topic=topic,
                type=type,
                value_units=value_units,
                array_size=array_size,
            )
            if array_size:
                stream.array_size = array_size
            if self.advanced_options_enabled:
                self._record_advanced_f142_values(stream)
        elif current_schema == WriterModules.EV42.value:
            stream = EV42Stream(parent_node=stream_group, source=source, topic=topic)
            if self.advanced_options_enabled:
                self._record_advanced_ev42_values(stream)
        elif current_schema == WriterModules.NS10.value:
            stream = NS10Stream(parent_node=stream_group, source=source, topic=topic)
        elif current_schema == WriterModules.SENV.value:
            stream = SENVStream(parent_node=stream_group, source=source, topic=topic)
        elif current_schema == WriterModules.HS00.value:
            stream = HS00Stream(  # type: ignore
                source=source,
                topic=topic,
                data_type=NotImplemented,
                edge_type=NotImplemented,
                error_type=NotImplemented,
                shape=[],
            )
        elif current_schema == WriterModules.TDCTIME.value:
            stream = TDCTStream(parent_node=stream_group, source=source, topic=topic)
        stream_group[group_name] = stream

        return stream_group

    def _record_advanced_f142_values(self, stream: F142Stream):
        """
        Save the advanced f142 properties to the stream data object.
        :param stream: The stream data object to be modified.
        """
        raise NotImplementedError

    def _record_advanced_ev42_values(self, stream: EV42Stream):
        """
        Save the advanced ev42 properties to the stream data object.
        :param stream: The stream data object to be modified.
        """
        stream.adc_pulse_debug = self.ev42_adc_pulse_debug_checkbox.isChecked()

    def fill_in_existing_ev42_fields(self, field: EV42Stream):
        """
        Fill in specific existing ev42 fields into the new UI field.
        :param field: The stream group
        """
        if check_if_advanced_options_should_be_enabled(
            [
                field.adc_pulse_debug,
            ]
        ):
            self._show_advanced_options(True)
            self._fill_existing_advanced_ev42_fields(field)

    def _fill_existing_advanced_ev42_fields(self, field: EV42Stream):
        """
        Fill the fields in the interface with the existing ev42 stream data.
        :param field: The ev42 stream data object.
        """
        self.ev42_adc_pulse_debug_checkbox.setChecked(field.adc_pulse_debug)

    def fill_in_existing_f142_fields(self, field: F142Stream):
        """
        Fill in specific existing f142 fields into the new UI field.
        :param field: The stream group
        """
        self.type_combo.setCurrentText(field.type)
        if field.array_size is not None:
            self.array_radio.setChecked(True)
            self.scalar_radio.setChecked(False)
            self.array_size_spinbox.setValue(field.array_size)
        else:
            self.array_radio.setChecked(False)
            self.scalar_radio.setChecked(True)
        if field.value_units is not None:
            self.value_units_edit.setText(field.value_units)

        if check_if_advanced_options_should_be_enabled([]):
            self._show_advanced_options(True)
            self._fill_existing_advanced_f142_fields(field)

    def _fill_existing_advanced_f142_fields(self, field: F142Stream):
        """
        Fill the advanced fields in the interface with the existing f142 stream data.
        :param field: The f412 stream data object.
        """
        raise NotImplementedError

    def update_existing_stream_info(self, field):
        """
        Fill in stream fields and properties into the new UI field.
        :param field: The stream group
        """
        field = field.children[
            0
        ]  # only the first stream in the stream group can be edited currently
        schema = field.writer_module
        self.schema_combo.setCurrentText(schema)
        self.topic_line_edit.setText(field.topic)
        self.source_line_edit.setText(field.source)
        if schema == WriterModules.F142.value:
            self.fill_in_existing_f142_fields(field)
        elif schema == WriterModules.EV42.value:
            self.fill_in_existing_ev42_fields(field)
