from nexus_constructor.component_fields import add_fields_to_component
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.component.component import Component
import numpy as np


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
    file = NexusWrapper("test_fields_1")

    component_group = file.nexus_file.create_group("test_component")
    component = Component(file, component_group)

    field_name = "test_field"
    field_dtype = np.float32
    field_value = field_dtype(32.123)

    field = DummyField(field_name, field_value, field_dtype)

    list_widget = DummyListWidget()
    list_widget.addItem(field)

    add_fields_to_component(component, list_widget)

    assert component.get_field(field_name)
    assert component.get_field(field_name).dtype == field_dtype
    assert component.get_field(field_name)[...] == field_value


def test_GIVEN_single_scalar_field_and_string_WHEN_adding_fields_to_component_THEN_field_appears_in_component_fields_with_correct_name_and_value():
    file = NexusWrapper("test_fields_2")

    component_group = file.nexus_file.create_group("test_component")
    component = Component(file, component_group)

    field_name = "test_field"
    field_value = np.string_(b"some_value")
    field = DummyField(field_name, field_value, field_value.dtype)

    list_widget = DummyListWidget()
    list_widget.addItem(field)

    add_fields_to_component(component, list_widget)

    assert component.get_field(field_name)
    assert bytes(component.get_field(field_name), encoding="ASCII") == field_value
