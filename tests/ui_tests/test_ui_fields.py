from PySide2.QtWidgets import QListWidget
import pytest
from mock import Mock
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_tree_model import ComponentTreeModel
from tests.test_utils import NX_CLASS_DEFINITIONS
import h5py
from PySide2.QtWidgets import QSpinBox
from nexus_constructor.field_utils import update_existing_stream_field
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.model.entry import Instrument
from nexus_constructor.stream_fields_widget import (
    check_if_advanced_options_should_be_enabled,
    StreamFieldsWidget,
    ADC_PULSE_DEBUG,
    NEXUS_INDICES_INDEX_EVERY_MB,
)


@pytest.fixture
def stream_fields_widget(qtbot, instrument, template):
    class DummyField:
        @property
        def name(self):
            return "test"

    add_component_dialog = AddComponentDialog(
        instrument, ComponentTreeModel(instrument), nx_classes=NX_CLASS_DEFINITIONS
    )
    add_component_dialog.setupUi(template)
    field = add_component_dialog.create_new_ui_field(DummyField())
    widget = StreamFieldsWidget(field.attrs_dialog)
    qtbot.addWidget(widget)
    return widget


def test_ui_field_GIVEN_field_has_units_filled_in_ui_WHEN_getting_field_group_THEN_units_are_stored_in_attrs(
    qtbot,
):
    listwidget = QListWidget()
    field = FieldWidget(["test"], listwidget)
    field_name = "test"
    field.name = field_name
    field.value_line_edit.setText("1")
    qtbot.addWidget(field)
    units = "m"
    field.units = units
    group = field.value

    assert group.contains_attribute("units")
    assert group.get_attribute_value("units") == units


def test_ui_field_GIVEN_field_does_not_have_units_filled_in_ui_WHEN_getting_field_group_THEN_units_are_not_saved(
    qtbot,
):
    listwidget = QListWidget()
    field = FieldWidget(["test"], listwidget)
    field_name = "test"
    field.name = field_name
    field.value_line_edit.setText("1")
    qtbot.addWidget(field)

    group = field.value

    assert not group.contains_attribute("units")


def test_ui_stream_field_GIVEN_f142_is_selected_WHEN_combo_is_changed_THEN_value_units_edit_is_shown(
    qtbot,
):
    listwidget = QListWidget()
    field = FieldWidget(["test"], listwidget)
    field_name = "test"
    field.name = field_name

    stream_fields_widget = StreamFieldsWidget(field)
    qtbot.addWidget(stream_fields_widget)

    stream_fields_widget.schema_combo.currentTextChanged.emit("f142")

    assert stream_fields_widget.value_units_edit.isEnabled()
    assert stream_fields_widget.value_units_label.isEnabled()


def test_ui_stream_field_GIVEN_f142_is_selected_WHEN_advanced_options_are_clicked_THEN_f142_group_box_is_shown(
    qtbot,
):
    listwidget = QListWidget()
    field = FieldWidget(["test"], listwidget)
    field_name = "test"
    field.name = field_name

    stream_fields_widget = StreamFieldsWidget(field)
    stream_fields_widget.schema_combo.setCurrentText("f142")

    qtbot.addWidget(stream_fields_widget)

    stream_fields_widget.f142_advanced_group_box.setVisible = Mock()
    stream_fields_widget._show_advanced_options(True)

    stream_fields_widget.f142_advanced_group_box.setVisible.assert_called_once_with(
        True
    )


def test_ui_stream_field_GIVEN_ev42_is_selected_WHEN_advanced_options_are_clicked_THEN_ev42_group_box_is_shown(
    qtbot,
):
    listwidget = QListWidget()
    field = FieldWidget(["test"], listwidget)
    field_name = "test"
    field.name = field_name

    stream_fields_widget = StreamFieldsWidget(field)
    stream_fields_widget.schema_combo.setCurrentText("ev42")

    qtbot.addWidget(stream_fields_widget)

    stream_fields_widget.ev42_advanced_group_box.setVisible = Mock()
    stream_fields_widget._show_advanced_options(True)

    stream_fields_widget.ev42_advanced_group_box.setVisible.assert_called_once_with(
        True
    )


def test_ui_stream_field_GIVEN_value_units_is_specified_WHEN_getting_stream_group_from_widget_THEN_value_units_appears_as_field(
    stream_fields_widget,
):
    value = "cubits"

    stream_fields_widget.schema_combo.setCurrentText("f142")
    stream_fields_widget.schema_combo.currentTextChanged.emit("f142")
    stream_fields_widget.value_units_edit.setText(value)

    group = stream_fields_widget.get_stream_group()
    field = group.children[0]
    assert value == field.value_units


def test_ui_stream_field_GIVEN_value_units_is_not_specified_WHEN_getting_stream_group_from_widget_THEN_value_units_does_not_appear_as_field(
    stream_fields_widget,
):
    stream_fields_widget.schema_combo.setCurrentText("f142")
    stream_fields_widget.schema_combo.currentTextChanged.emit("f142")
    stream_fields_widget.value_units_edit.setText("")

    group = stream_fields_widget.get_stream_group()
    field = group.children[0]
    assert not field.value_units


def test_GIVEN_advanced_option_in_field_WHEN_filling_in_advanced_options_THEN_spinbox_is_created(
    qtbot, file
):
    group = file.create_group("group")
    field_name = "test"

    advanced_options = [field_name]
    spinner = QSpinBox()

    items = {advanced_options[0]: spinner}.items()
    value = 4

    group.create_dataset(name=field_name, data=value)

    # fill_in_advanced_options(items, group)
    # Disabled whilst working on model change

    assert spinner.value() == value


def test_GIVEN_field_with_advanced_option_WHEN_checking_if_advanced_options_should_be_enabled_THEN_returns_true(
    file,
):

    group = file.create_group("group")

    field_name = "test"
    advanced_options = [field_name]
    group.create_dataset(name=field_name, data=1)
    assert check_if_advanced_options_should_be_enabled(advanced_options, group)


def test_GIVEN_field_without_advanced_option_WHEN_checking_if_advanced_options_should_be_enabled_THEN_returns_false(
    file,
):
    group = file.create_group("group")

    field_name = "test"
    advanced_options = ["not_test"]
    group.create_dataset(name=field_name, data=1)
    assert not check_if_advanced_options_should_be_enabled(advanced_options, group)


def test_GIVEN_element_that_has_not_been_filled_in_WHEN_creating_dataset_from_spinner_THEN_dataset_is_not_created(
    file, qtbot
):
    nexus_string = "advanced_option_1"
    spinner = QSpinBox()
    qtbot.addWidget(spinner)

    StreamFieldsWidget._create_dataset_from_spinner(file, {nexus_string: spinner})

    assert not file.keys()


def test_GIVEN_element_that_has_been_set_to_zero_in_WHEN_creating_dataset_from_spinner_THEN_dataset_is_not_created(
    file, qtbot
):
    nexus_string = "advanced_option_1"
    spinner = QSpinBox()
    spinner.setValue(0)
    qtbot.addWidget(spinner)

    StreamFieldsWidget._create_dataset_from_spinner(file, {nexus_string: spinner})

    assert not file.keys()


def test_GIVEN_element_that_has_been_filled_in_WHEN_creating_dataset_from_spinner_THEN_dataset_is_created(
    file, qtbot
):
    nexus_string = "advanced_option_1"
    spinner = QSpinBox()
    spinner.setValue(1024)
    qtbot.addWidget(spinner)

    StreamFieldsWidget._create_dataset_from_spinner(file, {nexus_string: spinner})

    assert nexus_string in file


@pytest.mark.skip(reason="Disabled whilst working on model change")
def test_GIVEN_stream_group_that_has_f142_advanced_option_WHEN_filling_in_existing_field_widget_THEN_f142_group_box_is_shown(
    file, qtbot, nexus_wrapper
):
    group = file.create_group("stream1")
    group.attrs["NX_class"] = "NCstream"

    vlen_str = h5py.special_dtype(vlen=str)
    group.create_dataset("writer_module", dtype=vlen_str, data="f142")
    group.create_dataset("type", dtype=vlen_str, data="byte")
    group.create_dataset("topic", dtype=vlen_str, data="topic1")
    group.create_dataset("source", dtype=vlen_str, data="source1")
    group.create_dataset(NEXUS_INDICES_INDEX_EVERY_MB, dtype=int, data=1)

    wrapper = nexus_wrapper
    wrapper.load_file(file, file)

    widget = FieldWidget()
    qtbot.addWidget(widget)

    update_existing_stream_field(group, widget)

    # this would usually be done outside of the update_existing_stream_field
    widget.name = group.name

    assert widget.streams_widget.f142_advanced_group_box.isEnabled()

    generated_group = widget.streams_widget.get_stream_group()
    assert generated_group["writer_module"][()] == group["writer_module"][()]
    assert generated_group["topic"][()] == group["topic"][()]
    assert generated_group["type"][()] == group["type"][()]
    assert generated_group["source"][()] == group["source"][()]
    assert (
        generated_group[NEXUS_INDICES_INDEX_EVERY_MB][()]
        == group[NEXUS_INDICES_INDEX_EVERY_MB][()]
    )


@pytest.mark.skip(reason="Disabled whilst working on model change")
def test_GIVEN_stream_group_that_has_ev42_advanced_option_WHEN_filling_in_existing_field_widget_THEN_ev42_group_box_is_shown(
    file, qtbot, nexus_wrapper
):
    group = file.create_group("stream2")
    group.attrs["NX_class"] = "NCstream"

    vlen_str = h5py.special_dtype(vlen=str)
    group.create_dataset("writer_module", dtype=vlen_str, data="ev42")
    group.create_dataset("topic", dtype=vlen_str, data="topic1")
    group.create_dataset("source", dtype=vlen_str, data="source1")
    group.create_dataset(ADC_PULSE_DEBUG, dtype=bool, data=True)

    wrapper = nexus_wrapper
    wrapper.load_file(file, file)

    instrument = Instrument(wrapper, {})

    widget = FieldWidget(instrument=instrument)
    qtbot.addWidget(widget)

    update_existing_stream_field(group, widget)

    # this would usually be done outside of the update_existing_stream_field
    widget.name = group.name

    assert widget.streams_widget.ev42_advanced_group_box.isEnabled()

    generated_group = widget.streams_widget.get_stream_group()
    assert generated_group["writer_module"][()] == group["writer_module"][()]
    assert generated_group["topic"][()] == group["topic"][()]
    assert generated_group["source"][()] == group["source"][()]
    assert generated_group[ADC_PULSE_DEBUG][()] == group[ADC_PULSE_DEBUG][()]


@pytest.mark.skip(reason="Disabled whilst working on model change")
def test_GIVEN_advanced_option_in_field_WHEN_filling_in_advanced_options_THEN_spinbox_is_created(
    qtbot, file
):
    group = file.create_group("group")
    field_name = "test"

    advanced_options = [field_name]
    spinner = QSpinBox()

    items = {advanced_options[0]: spinner}.items()
    value = 4

    group.create_dataset(name=field_name, data=value)

    # fill_in_advanced_options(items, group)
    # Disabled whilst working on model change

    assert spinner.value() == value


@pytest.mark.skip(reason="Disabled whilst working on model change")
def test_GIVEN_field_with_advanced_option_WHEN_checking_if_advanced_options_should_be_enabled_THEN_returns_true(
    file,
):

    group = file.create_group("group")

    field_name = "test"
    advanced_options = [field_name]
    group.create_dataset(name=field_name, data=1)
    assert check_if_advanced_options_should_be_enabled(advanced_options, group)


@pytest.mark.skip(reason="Disabled whilst working on model change")
def test_GIVEN_field_without_advanced_option_WHEN_checking_if_advanced_options_should_be_enabled_THEN_returns_false(
    file,
):
    group = file.create_group("group")

    field_name = "test"
    advanced_options = ["not_test"]
    group.create_dataset(name=field_name, data=1)
    assert not check_if_advanced_options_should_be_enabled(advanced_options, group)
