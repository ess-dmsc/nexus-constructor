import pytest
from mock import Mock
from PySide2.QtWidgets import QLabel, QListWidget

from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_tree_model import NexusTreeModel as ComponentTreeModel
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.model import Entry, Group
from nexus_constructor.stream_fields_widget import StreamFieldsWidget
from tests.test_utils import NX_CLASS_DEFINITIONS

POSSIBLE_FIELDS = [("test", "string", "")]


@pytest.fixture
def stream_fields_widget(qtbot, model, template):
    class DummyField:
        @property
        def name(self):
            return "test"

    entry = Entry()
    group = Group(name="some_name", parent_node=entry)
    entry.children.append(group)

    add_component_dialog = AddComponentDialog(
        None,
        model=model,
        component_model=ComponentTreeModel(model),
        nx_classes=NX_CLASS_DEFINITIONS,
        group_to_edit=group,
        scene_widget=None,
        initial_edit=False,
    )
    field = add_component_dialog.create_new_ui_field(DummyField())
    widget = StreamFieldsWidget(field.attrs_dialog)
    qtbot.addWidget(widget)
    return widget


def test_ui_field_GIVEN_field_has_units_filled_in_ui_WHEN_getting_field_group_THEN_units_are_stored_in_attrs(
    qtbot,
):
    listwidget = QListWidget()
    field = FieldWidget(None, POSSIBLE_FIELDS, listwidget)
    field_name = "test"
    field.name = field_name
    field.value_line_edit.setText("1")
    qtbot.addWidget(field)
    units = "m"
    field.units = units
    group = field.value

    assert group.attributes.contains_attribute("units")
    assert group.attributes.get_attribute_value("units") == units


def test_ui_field_GIVEN_field_does_not_have_units_filled_in_ui_WHEN_getting_field_group_THEN_units_are_not_saved(
    qtbot,
):
    listwidget = QListWidget()
    field = FieldWidget(None, POSSIBLE_FIELDS, listwidget)
    field_name = "test"
    field.name = field_name
    field.value_line_edit.setText("1")
    qtbot.addWidget(field)

    group = field.value

    assert not group.attributes.contains_attribute("units")


def test_ui_stream_field_GIVEN_f142_is_selected_WHEN_combo_is_changed_THEN_value_units_edit_is_shown(
    qtbot,
):
    listwidget = QListWidget()
    listwidget.field_name_edit = QLabel()
    field = FieldWidget(None, POSSIBLE_FIELDS, listwidget)
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
    listwidget.field_name_edit = QLabel()
    field = FieldWidget(None, POSSIBLE_FIELDS, listwidget)
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
    listwidget.field_name_edit = QLabel()
    field = FieldWidget(None, POSSIBLE_FIELDS, listwidget)
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

    stream = stream_fields_widget.get_stream_module(None)
    assert value == stream.value_units


def test_ui_stream_field_GIVEN_value_units_is_not_specified_WHEN_getting_stream_group_from_widget_THEN_value_units_does_not_appear_as_field(
    stream_fields_widget,
):
    stream_fields_widget.schema_combo.setCurrentText("f142")
    stream_fields_widget.schema_combo.currentTextChanged.emit("f142")
    stream_fields_widget.value_units_edit.setText("")

    stream = stream_fields_widget.get_stream_module(None)
    assert not stream.value_units
