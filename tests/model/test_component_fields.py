import numpy as np

from nexus_constructor.add_component_window import add_fields_to_component
from nexus_constructor.model.component import Component
from nexus_constructor.model.module import Dataset


class DummyListWidget:
    widgets = []

    def addItem(self, widget):
        self.widgets.append(widget)

    def count(self):
        return len(self.widgets)

    def item(self, i):
        return self.widgets[i]

    def itemWidget(self, widget):
        return widget


class DummyField:
    def __init__(self, name, value, dtype):
        self.name = name
        self.value = value
        self.dtype = dtype


def test_GIVEN_single_scalar_field_and_float_WHEN_adding_fields_to_component_THEN_field_appears_in_component_fields_with_correct_name_and_value():
    component = Component("test_component")

    field_name = "test_field"
    field_dtype = np.float32
    field_value_raw = field_dtype(32.123)

    field_value = Dataset(
        parent_node=component,
        name=field_name,
        type=field_dtype,
        values=field_value_raw,
    )

    field = DummyField(field_name, field_value, field_dtype)

    list_widget = DummyListWidget()
    list_widget.addItem(field)

    add_fields_to_component(component, list_widget)

    # Test the __contains__ operator
    assert field_name in component

    assert component.get_field_value(field_name) == field_value_raw


def test_GIVEN_single_scalar_field_and_string_WHEN_adding_fields_to_component_THEN_field_appears_in_component_fields_with_correct_name_and_value():
    component = Component("test_component")
    field_name = "test_field"
    field_value_raw = np.string_(b"some_value")

    field_value = Dataset(
        parent_node=component,
        name=field_name,
        type=str,
        values=field_value_raw,
    )

    field = DummyField(field_name, field_value, str)
    list_widget = DummyListWidget()
    list_widget.addItem(field)

    add_fields_to_component(component, list_widget)

    assert field_name in component
    assert component.get_field_value(field_name) == field_value_raw
