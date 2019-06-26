from nexus_constructor.component import ComponentModel
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from cmath import isclose
from typing import Any


def _create_file_containing_test_component(
    field_name: str, field_value: Any, component_name: str = "test_component"
):
    nexus_wrapper = NexusWrapper("test_file.nxs")
    component_group = nexus_wrapper.nexus_file.create_group(component_name)
    component_group.create_dataset(field_name, data=field_value)
    return nexus_wrapper, component_group


def test_can_create_and_read_from_field_in_component():
    field_name = "some_field"
    field_value = 42
    nexus_wrapper, component_group = _create_file_containing_test_component(
        field_name, field_value
    )
    component = ComponentModel(nexus_wrapper, component_group)
    returned_value = component.get_field(field_name)
    assert (
        returned_value == field_value
    ), "Expected to get same value back from field as it was created with"


def test_nameerror_raised_if_requested_field_does_not_exist():
    field_name = "some_field"
    field_value = 42
    nexus_wrapper, component_group = _create_file_containing_test_component(
        field_name, field_value
    )
    component = ComponentModel(nexus_wrapper, component_group)
    try:
        component.get_field("nonexistent_field")
    except NameError:
        pass  # as expected


def test_created_component_has_specified_name():
    name = "component_name"
    field_name = "some_field"
    field_value = 42
    nexus_wrapper, component_group = _create_file_containing_test_component(
        field_name, field_value, name
    )
    component = ComponentModel(nexus_wrapper, component_group)
    assert component.name == name


def test_component_can_be_renamed():
    initial_name = "component_name"
    field_name = "some_field"
    field_value = 42
    nexus_wrapper, component_group = _create_file_containing_test_component(
        field_name, field_value, initial_name
    )
    component = ComponentModel(nexus_wrapper, component_group)
    assert component.name == initial_name
    new_name = "new_name"
    component.name = new_name
    assert component.name == new_name


def test_value_of_field_can_be_changed():
    name = "component_name"
    field_name = "some_field"
    initial_value = 42
    nexus_wrapper, component_group = _create_file_containing_test_component(
        field_name, initial_value, name
    )
    component = ComponentModel(nexus_wrapper, component_group)
    returned_value = component.get_field(field_name)
    assert (
        returned_value == initial_value
    ), "Expected to get same value back from field as it was created with"
    new_value = 13
    component.set_field("some_field", new_value, dtype=int)
    returned_value = component.get_field(field_name)
    assert (
        returned_value == new_value
    ), "Expected to get same value back from field as it was changed to"


def test_type_of_field_can_be_changed():
    """
    This is important to test because the implementation is very different to just changing the value.
    When the type changes the dataset has to be deleted and recreated with the new type
    """

    name = "component_name"
    field_name = "some_field"
    initial_value = 42
    nexus_wrapper, component_group = _create_file_containing_test_component(
        field_name, initial_value, name
    )
    component = ComponentModel(nexus_wrapper, component_group)
    returned_value = component.get_field(field_name)
    assert (
        returned_value == initial_value
    ), "Expected to get same value back from field as it was created with"

    new_value = 17.3
    component.set_field("some_field", new_value, dtype=float)
    returned_value = component.get_field(field_name)
    assert isclose(
        returned_value, new_value
    ), "Expected to get same value back from field as it was changed to"
