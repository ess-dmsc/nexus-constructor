from functools import partial
from typing import List, Tuple

import numpy as np
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from nexus_constructor.array_dataset_table_widget import ValueDelegate
from nexus_constructor.common_attrs import AD_ARRAY_SIZE_PLACEHOLDER, ARRAY, SCALAR
from nexus_constructor.model.group import Group
from nexus_constructor.model.module import (
    ADC_PULSE_DEBUG,
    CHUNK_SIZE,
    CUE_INTERVAL,
    ADARStream,
    EV42Stream,
    EV44Stream,
    F142Stream,
    HS01Shape,
    HS01Stream,
    NS10Stream,
    SENVStream,
    StreamModule,
    StreamModules,
    TDCTStream,
    WriterModules,
)
from nexus_constructor.ui_utils import validate_general_widget, validate_line_edit
from nexus_constructor.validators import (
    NoEmptyStringValidator,
    SchemaSelectionValidator,
    StreamWidgetValidator,
)
from nexus_constructor.widgets.dropdown_list import DropDownList

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


class HS01Dialog(QDialog):
    """
    Dialog for HS01 advanced options.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Advanced options for hs01 schema")
        self.setLayout(QVBoxLayout())
        self.hs01_advanced_opts: Tuple[List[HS01Shape], str, str, str] = None
        self.shape_table = QTableWidget(0, 4)
        self.shape_table.setParent(self)
        self.shape_table.setHorizontalHeaderLabels(
            ["label", "unit", "edges", "dataset_name"]
        )
        self.data_type_edit = QLineEdit()
        self.error_type_edit = QLineEdit()
        self.edge_type_edit = QLineEdit()
        self.setupUi()

    def setupUi(self):
        add_shape_button = QPushButton(text="Add shape")
        remove_shape_button = QPushButton(text="Remove shape")
        label_height = 15
        data_type_label = QLabel("Data type:")
        data_type_label.setFixedHeight(label_height)
        error_type_label = QLabel("Error type:")
        error_type_label.setFixedHeight(label_height)
        edge_type_label = QLabel("Edge type:")
        edge_type_label.setFixedHeight(label_height)
        ok_button = QPushButton(text="Done")

        self.setFixedWidth(self.shape_table.width())
        add_shape_button.clicked.connect(self._add_shape)
        remove_shape_button.clicked.connect(self._remove_shape)
        ok_button.clicked.connect(self._on_ok_hs01_advanced_opts)

        self.layout().addWidget(add_shape_button, 0)
        self.layout().addWidget(remove_shape_button, 1)
        self.layout().addWidget(self.shape_table, 2)
        self.layout().addWidget(data_type_label, 3)
        self.layout().addWidget(self.data_type_edit, 4)
        self.layout().addWidget(error_type_label, 5)
        self.layout().addWidget(self.error_type_edit, 6)
        self.layout().addWidget(edge_type_label, 7)
        self.layout().addWidget(self.edge_type_edit, 8)
        self.layout().addWidget(ok_button, 9)

    def _add_shape(self):
        self.shape_table.insertRow(self.shape_table.rowCount())

    def _remove_shape(self):
        self.shape_table.removeRow(self.shape_table.currentRow())

    def _on_ok_hs01_advanced_opts(self):
        data_type = self.data_type_edit.text() if self.data_type_edit else None
        error_type = self.error_type_edit.text() if self.error_type_edit else None
        edge_type = self.edge_type_edit.text() if self.edge_type_edit else None
        self.hs01_advanced_opts = (
            self._extract_shape_data(),
            data_type,
            error_type,
            edge_type,
        )
        self.setVisible(False)

    def _extract_shape_data(self) -> List[HS01Shape]:
        shapes: List[HS01Shape] = []
        for row in range(self.shape_table.rowCount()):
            edge_extraction_fail = False
            label = self.shape_table.item(row, 0).text()
            unit = self.shape_table.item(row, 1).text()
            edges_text_list = self.shape_table.item(row, 2).text().split(",")
            edges = []
            for edge in edges_text_list:
                try:
                    edges.append(int(edge))
                except ValueError:
                    edge_extraction_fail = True
                    print(f"Edge extraction failed: {edge} is not an integer.")
            dataset_name = self.shape_table.item(row, 3).text()
            if not edge_extraction_fail:
                size = len(edges) - 1
                shapes.append(HS01Shape(size, label, unit, edges, dataset_name))
        return shapes

    def fill_existing_advanced_hs01_fields(self, field: HS01Stream):
        self.data_type_edit.setText(field.type)
        self.edge_type_edit.setText(field.edge_type)
        self.error_type_edit.setText(field.error_type)
        self._fill_in_hs01_shape(field.shape)

    def _fill_in_hs01_shape(self, shapes: List[HS01Shape]):
        for shape in shapes:
            self.shape_table.insertRow(self.shape_table.rowCount())
            row = self.shape_table.rowCount() - 1
            self.shape_table.setItem(row, 0, QTableWidgetItem(shape.label))
            self.shape_table.setItem(row, 1, QTableWidgetItem(shape.unit))
            edges_text = [str(val) for val in shape.edges]
            self.shape_table.setItem(row, 2, QTableWidgetItem(",".join(edges_text)))
            self.shape_table.setItem(row, 3, QTableWidgetItem(shape.dataset_name))

    def get_advanced_hs01_options(self):
        return self.hs01_advanced_opts


class StreamFieldsWidget(QDialog):
    """
    A stream widget containing schema-specific properties.
    """

    def __init__(
        self,
        parent,
        show_only_f142_stream: bool = False,
        node_parent: Group = None,
    ):
        super().__init__()
        self.setParent(parent)
        self.setLayout(QGridLayout())
        self.setWindowModality(Qt.WindowModal)
        self.setModal(True)

        self._node_parent = node_parent
        self._show_only_f142_stream = show_only_f142_stream
        self.minimum_spinbox_value = 0
        self.maximum_spinbox_value = 100_000_000
        self.advanced_options_enabled = False

        self.schema_label = QLabel("Schema: ")
        self.schema_combo = DropDownList()
        self.schema_validator = SchemaSelectionValidator()
        self.schema_combo.setValidator(self.schema_validator)
        self.schema_validator.is_valid.connect(
            partial(validate_general_widget, self.schema_combo)
        )

        self.topic_label = QLabel("Topic: ")
        self.topic_line_edit = QLineEdit()
        self.topic_validator = NoEmptyStringValidator()
        self.topic_line_edit.setValidator(self.topic_validator)
        self.topic_validator.is_valid.connect(
            partial(
                validate_line_edit,
                self.topic_line_edit,
                tooltip_on_reject="Topic name can not be empty.",
            )
        )
        validate_line_edit(self.topic_line_edit, False)

        self.source_label = QLabel("Source: ")
        self.source_line_edit = QLineEdit()
        self.source_validator = NoEmptyStringValidator()
        self.source_line_edit.setValidator(self.source_validator)
        self.source_validator.is_valid.connect(
            partial(
                validate_line_edit,
                self.source_line_edit,
                tooltip_on_reject="Source name can not be empty.",
            )
        )
        validate_line_edit(self.source_line_edit, False)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.parent().close)
        self.cancel_button = QPushButton("Cancel")

        self.ok_validator = StreamWidgetValidator()
        self.ok_validator.is_valid.connect(self.ok_button.setEnabled)
        self.topic_line_edit.validator().is_valid.connect(
            self.ok_validator.set_topic_valid
        )
        self.source_line_edit.validator().is_valid.connect(
            self.ok_validator.set_source_valid
        )
        self.schema_combo.validator().is_valid.connect(
            self.ok_validator.set_schema_valid
        )

        self.array_size_label = QLabel("Array size: ")
        self.array_size_spinbox = QSpinBox()
        self.array_size_spinbox.setMaximum(np.iinfo(np.int32).max)
        self.array_size_placeholder_label = QLabel("Use placeholder:")
        self.array_size_placeholder = QCheckBox()
        self.array_size_placeholder.clicked.connect(self._hide_array_size_table)

        self.array_size_table = QTableWidget(1, 3)
        self.array_size_table.setHorizontalHeaderLabels(["x", "y", "z"])
        self.array_size_table.setVerticalHeaderLabels([""])
        table_height = self.array_size_table.sizeHintForRow(
            0
        ) + self.array_size_table.sizeHintForRow(1)
        self.array_size_table.setMaximumHeight(table_height)
        self.array_size_table.setFrameStyle(QFrame.NoFrame)
        self.array_size_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.array_size_table.resizeColumnsToContents()
        self.array_size_table.resizeRowsToContents()
        self.array_size_table.setItemDelegate(ValueDelegate(int, self.array_size_table))

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

        self._old_schema = None
        self.__add_items_to_schema_combo()
        self.schema_combo.setCurrentText(StreamModules.F142.value)
        self.ok_button.clicked.connect(self._update_possible_stream_modules)

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
        self.layout().addWidget(self.array_size_table, 6, 1)
        self.layout().addWidget(self.array_size_placeholder_label, 7, 0)
        self.layout().addWidget(self.array_size_placeholder, 7, 1)

        # Spans both rows
        self.layout().addWidget(self.show_advanced_options_button, 8, 0, 1, 2)
        self.layout().addWidget(self.f142_advanced_group_box, 9, 0, 1, 2)
        self.layout().addWidget(self.ev42_advanced_group_box, 10, 0, 1, 2)

        self.layout().addWidget(self.ok_button, 12, 0, 1, 2)
        self.layout().addWidget(self.cancel_button, 13, 0, 1, 2)

        # hs01 schema advanced options dialog.
        self.hs01_advanced_dialog = HS01Dialog(self)

        self.schema_combo.currentTextChanged.connect(self._schema_type_changed)
        self._schema_type_changed(self.schema_combo.currentText())
        self.parent().parent().field_name_edit.setVisible(False)

    def _add_items_to_schema_combo(self):
        self.schema_combo.currentTextChanged.disconnect(self._schema_type_changed)
        self.__add_items_to_schema_combo()
        self.schema_combo.setCurrentText(self._old_schema)
        self.schema_combo.currentTextChanged.connect(self._schema_type_changed)

    def __add_items_to_schema_combo(self):
        self.schema_combo.clear()
        if self._show_only_f142_stream:
            self.schema_combo.addItems([StreamModules.F142.value])
        elif self._node_parent:
            possible_stream_modules = (
                self._node_parent.get_possible_stream_modules().copy()
            )
            if self._old_schema:
                possible_stream_modules.append(self._old_schema)
            self.schema_combo.addItems(list(set(possible_stream_modules)))
        else:
            self.schema_combo.addItems([e.value for e in StreamModules])

    def update_schema_combo(self):
        self.update_node_parent_reference()
        if self._old_schema:
            self._node_parent.add_stream_module(self._old_schema)
        self._add_items_to_schema_combo()

    def update_node_parent_reference(self):
        if not self._node_parent:
            self._node_parent = self.parent().parent()._node_parent

    def _update_possible_stream_modules(self):
        self.update_node_parent_reference()
        new_schema = self.schema_combo.currentText()
        if self._old_schema:
            self._node_parent.add_stream_module(self._old_schema)
        self._node_parent.remove_stream_module(new_schema)
        self._old_schema = new_schema

    def reset_possible_stream_modules(self):
        self.update_node_parent_reference()
        self._node_parent.remove_stream_module(self._old_schema)

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

        self.ev42_chunk_size_spinner = (
            self.create_label_and_spinbox_for_advanced_option(
                CHUNK_SIZE, self.ev42_advanced_group_box
            )
        )
        self.ev42_cue_interval_spinner = (
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
        self.f142_chunk_size_spinner = (
            self.create_label_and_spinbox_for_advanced_option(
                CHUNK_SIZE, self.f142_advanced_group_box
            )
        )
        self.f142_cue_interval_spinner = (
            self.create_label_and_spinbox_for_advanced_option(
                CUE_INTERVAL, self.f142_advanced_group_box
            )
        )

    def _show_advanced_options(self, show):
        schema = self.schema_combo.currentText()
        if schema == WriterModules.F142.value:
            self.f142_advanced_group_box.setVisible(show)
        elif schema in [WriterModules.EV42.value, WriterModules.EV44.value]:
            self.ev42_advanced_group_box.setVisible(show)
        elif schema == WriterModules.HS01.value:
            self.hs01_advanced_dialog.setVisible(show)
            self.hs01_advanced_dialog.show()
        self.advanced_options_enabled = show

    def _show_array_size(self, show: bool):
        self.array_size_spinbox.setVisible(show)
        self.array_size_label.setVisible(show)

    def _schema_type_changed(self, schema: str):
        self.parent().setWindowTitle(f"Editing {schema} stream field")
        self.show_advanced_options_button.setText("Show/hide advanced options")
        self.f142_advanced_group_box.setVisible(False)
        self.ev42_advanced_group_box.setVisible(False)
        self.hs01_advanced_dialog.setVisible(False)
        self.show_advanced_options_button.setVisible(False)
        self.show_advanced_options_button.setChecked(False)
        self.value_units_label.setVisible(False)
        self.value_units_edit.setVisible(False)
        self._show_array_size_table(False)
        if schema == WriterModules.F142.value:
            self.value_units_label.setVisible(True)
            self.value_units_edit.setVisible(True)
            self._set_edits_visible(True, True)
            self.show_advanced_options_button.setVisible(True)
            self.f142_advanced_group_box.setVisible(False)
        elif schema in [WriterModules.EV42.value, WriterModules.EV44.value]:
            self._set_edits_visible(True, False)
            self.show_advanced_options_button.setVisible(True)
            self.ev42_advanced_group_box.setVisible(False)
        elif schema == WriterModules.ADAR.value:
            self._set_edits_visible(True, False)
            self._show_array_size_table(True)
            self.ev42_advanced_group_box.setVisible(False)
            self._hide_array_size_table()
        elif schema == WriterModules.HS01.value:
            self.show_advanced_options_button.setText("Show advanced options dialog")
            self._set_edits_visible(True, False)
            self.show_advanced_options_button.setVisible(True)
        elif schema == WriterModules.NS10.value:
            self._set_edits_visible(True, False, "nicos/<device>/<parameter>")
        elif (
            schema == WriterModules.TDCTIME.value or schema == WriterModules.SENV.value
        ):
            self._set_edits_visible(True, False)

    def _show_array_size_table(self, show: bool):
        self.array_size_label.setVisible(show)
        self.array_size_table.setVisible(show)
        self.array_size_placeholder.setVisible(show)
        self.array_size_placeholder_label.setVisible(show)

    def _hide_array_size_table(self):
        show = not self.array_size_placeholder.isChecked()
        self.array_size_table.setDisabled(not show)
        self.array_size_table.setVisible(show)

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

    def get_stream_module(self, parent) -> StreamModule:
        """
        Create the stream module
        :return: The created stream module
        """

        source = self.source_line_edit.text()
        topic = self.topic_line_edit.text()
        stream: StreamModule = None
        type = self.type_combo.currentText()
        current_schema = self.schema_combo.currentText()
        if current_schema == WriterModules.F142.value:
            value_units = self.value_units_edit.text()
            array_size = self.array_size_spinbox.value()
            stream = F142Stream(
                parent_node=parent,
                source=source,
                topic=topic,
                type=type,
                value_units=value_units,
                array_size=array_size,
            )
            if array_size:
                stream.array_size = array_size
            if self.advanced_options_enabled:
                self.record_advanced_f142_values(stream)
        elif current_schema == WriterModules.ADAR.value:
            array_size = []
            if self.array_size_placeholder.isChecked():
                array_size = AD_ARRAY_SIZE_PLACEHOLDER
            else:
                for i in range(self.array_size_table.columnCount()):
                    table_value = self.array_size_table.item(0, i)
                    if table_value:
                        array_size.append(int(table_value.text()))
            stream = ADARStream(parent_node=parent, source=source, topic=topic)
            stream.array_size = array_size
        elif current_schema in [WriterModules.EV42.value, WriterModules.EV44.value]:
            if current_schema == WriterModules.EV42.value:
                stream = EV42Stream(parent_node=parent, source=source, topic=topic)
            else:
                stream = EV44Stream(parent_node=parent, source=source, topic=topic)
            if self.advanced_options_enabled:
                self.record_advanced_ev42_values(stream)
        elif current_schema == WriterModules.NS10.value:
            stream = NS10Stream(parent_node=parent, source=source, topic=topic)
        elif current_schema == WriterModules.SENV.value:
            stream = SENVStream(parent_node=parent, source=source, topic=topic)
        elif current_schema == WriterModules.HS01.value:
            stream = HS01Stream(  # type: ignore
                parent_node=parent,
                source=source,
                topic=topic,
            )
            self.record_advanced_hs01_values(stream)
        elif current_schema == WriterModules.TDCTIME.value:
            stream = TDCTStream(parent_node=parent, source=source, topic=topic)

        return stream

    def record_advanced_hs01_values(self, stream: HS01Stream):
        """
        Save the advanced hs01 properties to the stream data object.
        :param stream: The stream data object to be modified.
        """
        hs01_advanced_opts = self.hs01_advanced_dialog.get_advanced_hs01_options()
        if not hs01_advanced_opts:
            return
        shape, data_type, error_type, edge_type = hs01_advanced_opts
        stream.shape = shape
        stream.type = data_type
        stream.edge_type = edge_type
        stream.error_type = error_type

    def record_advanced_f142_values(self, stream: F142Stream):
        """
        Save the advanced f142 properties to the stream data object.
        :param stream: The stream data object to be modified.
        """
        stream.chunk_size = self.f142_chunk_size_spinner.value()
        stream.cue_interval = self.f142_cue_interval_spinner.value()

    def record_advanced_ev42_values(self, stream: EV42Stream):
        """
        Save the advanced ev42 properties to the stream data object.
        :param stream: The stream data object to be modified.
        """
        stream.adc_pulse_debug = self.ev42_adc_pulse_debug_checkbox.isChecked()
        stream.chunk_size = self.ev42_chunk_size_spinner.value()
        stream.cue_interval = self.ev42_cue_interval_spinner.value()

    def fill_in_existing_ev42_fields(self, field: EV42Stream):
        """
        Fill in specific existing ev42 fields into the new UI field.
        :param field: The stream group
        """
        if check_if_advanced_options_should_be_enabled(
            [field.adc_pulse_debug, field.chunk_size, field.cue_interval]
        ):
            self._show_advanced_options(True)
            self._fill_existing_advanced_ev42_fields(field)

    def _fill_existing_advanced_ev42_fields(self, field: EV42Stream):
        """
        Fill the fields in the interface with the existing ev42 stream data.
        :param field: The ev42 stream data object.
        """
        self.ev42_adc_pulse_debug_checkbox.setChecked(field.adc_pulse_debug)
        self.ev42_chunk_size_spinner.setValue(field.chunk_size)
        self.ev42_cue_interval_spinner.setValue(field.cue_interval)

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

        if check_if_advanced_options_should_be_enabled(
            [field.chunk_size, field.cue_interval]
        ):
            self._show_advanced_options(True)
            self._fill_existing_advanced_f142_fields(field)

    def _fill_existing_advanced_f142_fields(self, field: F142Stream):
        """
        Fill the advanced fields in the interface with the existing f142 stream data.
        :param field: The f412 stream data object.
        """
        self.f142_chunk_size_spinner.setValue(field.chunk_size)
        self.f142_cue_interval_spinner.setValue(field.cue_interval)

    def update_existing_stream_info(self, field):
        """
        Fill in stream fields and properties into the new UI field.
        :param field: The stream group
        """
        if not field:
            raise TypeError("Field is NoneType when expecting type StreamModule.")
        if isinstance(field, Group):
            field = field.children[0]
        if hasattr(field, "parent_node") and isinstance(field.parent_node, Group):
            self.schema_validator.set_group(field.parent_node)
        else:
            self.schema_validator.set_group(None)
        schema = field.writer_module

        # Needed to correctly add the used schema when the module was created
        # from the group editor.
        self._old_schema = schema
        self.update_node_parent_reference()
        self.__add_items_to_schema_combo()
        self.schema_combo.setCurrentText(schema)

        self.schema_validator.validate(schema, 0)
        self.topic_line_edit.setText(field.topic)
        self.topic_validator.validate(field.topic, 0)
        self.source_line_edit.setText(field.source)
        self.source_validator.validate(field.source, 0)
        if schema == WriterModules.F142.value:
            self.fill_in_existing_f142_fields(field)
        elif schema in [WriterModules.EV42.value, WriterModules.EV44.value]:
            self.fill_in_existing_ev42_fields(field)
        elif schema == WriterModules.ADAR.value:
            if field.array_size == AD_ARRAY_SIZE_PLACEHOLDER:
                self.array_size_placeholder.setChecked(True)
                self._hide_array_size_table()
            elif not field.array_size:
                field.array_size = AD_ARRAY_SIZE_PLACEHOLDER
                self.array_size_placeholder.setChecked(True)
                self._hide_array_size_table()
            else:
                for i, val in enumerate(field.array_size):
                    self.array_size_table.setItem(0, i, QTableWidgetItem(str(val)))
        elif schema == WriterModules.HS01.value:
            self.hs01_advanced_dialog.fill_existing_advanced_hs01_fields(field)
