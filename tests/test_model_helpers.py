from nexus_constructor.model.component import Component
from nexus_constructor.model.helpers import get_item, set_item, remove_item
import pytest


def test_get_item_returns_correct_component_when_given_component_is_in_list():
    name = "component1"
    test = Component(name)

    list_of_components = [test]
    assert get_item(list_of_components, name) == test


def test_get_item_throws_error_when_component_is_not_in_list_then_works_when_item_is_set():
    name = "component1"
    test = Component(name)

    list_of_components = []

    with pytest.raises(TypeError):
        assert get_item(list_of_components, name)

    set_item(list_of_components, name, test)
    assert get_item(list_of_components, name) == test


def test_remove_item_removes_item_from_list():
    name = "component1"
    test = Component(name)

    list_of_components = [test]

    remove_item(list_of_components, name)

    assert not list_of_components


def test_remove_item_removes_single_item_in_list_and_not_everything():
    comp1_name = "component1"
    comp1 = Component(comp1_name)

    comp2_name = "component2"
    comp2 = Component(comp2_name)

    list_of_components = [comp1, comp2]
    remove_item(list_of_components, comp1_name)

    assert list_of_components == [comp2]


def test_set_item_works_on_list_that_has_components_in():
    comp1_name = "component1"
    comp1 = Component(comp1_name)

    list_of_components = [comp1]

    comp2_name = "component2"
    comp2 = Component(comp2_name)

    set_item(list_of_components, comp2_name, comp2)

    assert list_of_components == [comp1, comp2]


def test_remove_item_on_empty_list_throws_type_error():
    list_of_components = []

    with pytest.raises(TypeError):
        remove_item(list_of_components, "test")


def test_remove_item_on_populated_list_without_item_in_throws_type_error():
    comp1_name = "component1"
    comp1 = Component(comp1_name)
    comp2_name = "component2"
    comp2 = Component(comp2_name)

    list_of_components = [comp1, comp2]
    with pytest.raises(TypeError):
        remove_item(list_of_components, "test")


def test_set_item_with_existing_component_in_overwrites_if_name_is_same():
    comp1_name = "component1"
    comp1 = Component(comp1_name)

    comp2 = Component(comp1_name)
    nx_class = "NXaperture"
    comp2.nx_class = nx_class

    list_of_components = [comp1]

    set_item(list_of_components, comp1_name, comp2)

    assert list_of_components[0].nx_class.values == nx_class
