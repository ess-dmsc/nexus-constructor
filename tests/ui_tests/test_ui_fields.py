from PySide2.QtWidgets import QListWidget
import pytest

from nexus_constructor.component_fields import FieldWidget
from nexus_constructor.stream_fields_widget import StreamFieldsWidget
from tests.ui_tests.test_ui_add_component_window import (  # noqa: F401
    add_component_dialog,
)


@pytest.fixture
def create_stream_widget(add_component_dialog):
    class DummyField:
        @property
        def name(self):
            return "test"

    field = add_component_dialog.create_new_ui_field(DummyField())
    widget = StreamFieldsWidget(field.attrs_dialog)
    return widget


def test_ui_stream_field_GIVEN_f142_is_selected_WHEN_combo_is_changed_THEN_value_units_edit_is_shown(
    qtbot
):
    listwidget = QListWidget()
    field = FieldWidget(["test"], listwidget)
    field_name = "test"
    field.name = field_name

    widget = StreamFieldsWidget(field)

    qtbot.addWidget(widget)

    widget.schema_combo.currentTextChanged.emit("f142")

    assert widget.value_units_edit.isEnabled()
    assert widget.value_units_label.isEnabled()


def test_ui_stream_field_GIVEN_value_units_is_specified_WHEN_getting_stream_group_from_widget_THEN_value_units_appears_as_field(
    qtbot, create_stream_widget
):

    widget = create_stream_widget

    qtbot.addWidget(widget)
    value = "cubits"

    widget.schema_combo.setCurrentText("f142")
    widget.schema_combo.currentTextChanged.emit("f142")
    widget.value_units_edit.setText(value)

    group = widget.get_stream_group()
    assert value == group["value_units"][()]


def test_ui_stream_field_GIVEN_value_units_is_not_specified_WHEN_getting_stream_group_from_widget_THEN_value_units_does_not_appear_as_field(
    qtbot, create_stream_widget
):

    widget = create_stream_widget

    qtbot.addWidget(widget)

    widget.schema_combo.setCurrentText("f142")
    widget.schema_combo.currentTextChanged.emit("f142")
    widget.value_units_edit.setText("")

    group = widget.get_stream_group()
    assert "value_units" not in group
