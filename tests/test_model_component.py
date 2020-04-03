import pytest
from nexus_constructor.model.component import Component


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

    assert comp.description.values == description
