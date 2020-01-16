from PySide2.QtWidgets import QListWidget
import pytest

from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_fields import FieldWidget
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.stream_fields_widget import StreamFieldsWidget
from tests.test_utils import DEFINITIONS_DIR


@pytest.fixture
def stream_fields_widget(qtbot, instrument, template):
    class DummyField:
        @property
        def name(self):
            return "test"

    add_component_dialog = AddComponentDialog(
        instrument, ComponentTreeModel(instrument), definitions_dir=DEFINITIONS_DIR
    )
    add_component_dialog.setupUi(template)
    field = add_component_dialog.create_new_ui_field(DummyField())
    widget = StreamFieldsWidget(field.attrs_dialog)
    qtbot.addWidget(widget)
    return widget


def test_ui_stream_field_GIVEN_f142_is_selected_WHEN_combo_is_changed_THEN_value_units_edit_is_shown(
    qtbot
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


def test_ui_stream_field_GIVEN_value_units_is_specified_WHEN_getting_stream_group_from_widget_THEN_value_units_appears_as_field(
    stream_fields_widget
):
    value = "cubits"

    stream_fields_widget.schema_combo.setCurrentText("f142")
    stream_fields_widget.schema_combo.currentTextChanged.emit("f142")
    stream_fields_widget.value_units_edit.setText(value)

    group = stream_fields_widget.get_stream_group()
    assert value == group["value_units"][()]


def test_ui_stream_field_GIVEN_value_units_is_not_specified_WHEN_getting_stream_group_from_widget_THEN_value_units_does_not_appear_as_field(
    stream_fields_widget
):
    stream_fields_widget.schema_combo.setCurrentText("f142")
    stream_fields_widget.schema_combo.currentTextChanged.emit("f142")
    stream_fields_widget.value_units_edit.setText("")

    group = stream_fields_widget.get_stream_group()
    assert "value_units" not in group
