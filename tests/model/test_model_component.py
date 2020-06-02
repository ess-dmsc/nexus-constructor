import pytest
from nexus_constructor.model.component import Component
import numpy as np


def test_component_set_item_with_brackets_works_with_another_component():
    comp1 = Component("comp1")
    comp2 = Component("comp2")
    comp1[comp2.name] = comp2

    assert comp1[comp2.name] == comp2


def test_component_set_item_with_brackets_throws_when_string_is_entered():
    comp1 = Component("comp1")
    some_field_value = "test"
    with pytest.raises(AttributeError):
        comp1["some_field"] = some_field_value
        assert comp1["some_field"] == some_field_value


def test_component_set_description_correctly_sets_description():
    comp = Component("comp3")
    description = "a component"
    comp.description = description

    assert comp.description == description


def test_component_set_field_with_numpy_array_correctly_sets_field_value():

    comp = Component("comp4")
    data = [[1], [2]]
    dtype = np.int
    field_name = "field1"
    field_value = np.asarray(data, dtype=np.int)

    comp.set_field_value(field_name, field_value, dtype)

    field_dataset = comp["field1"]
    assert field_dataset.name == field_name
    assert np.array_equal(field_dataset.values, field_value)
    assert field_dataset.dataset.size == 2
    assert field_dataset.dataset.type == dtype


def test_component_set_field_with_scalar_value_correctly_sets_field_value():
    comp = Component("comp4")
    field_name = "testfield"
    data = 123
    dtype = np.int

    comp.set_field_value(field_name, data, dtype)

    field_dataset = comp[field_name]

    assert field_dataset.name == field_name
    assert field_dataset.values == data
    assert field_dataset.dataset.size == [1]
    assert field_dataset.dataset.type == dtype
