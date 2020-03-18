from nexus_constructor.model.component import Component
from nexus_constructor.model.helpers import get_item, set_item, remove_item
import pytest


def test_get_item_works_as_expected_when_component_is_in_list():
    name = "component1"
    test = Component(name)

    list_of_components = [test]
    assert get_item(list_of_components, name) == test


def test_get_item_works_as_expected_when_component_is_not_in_list_then_works_when_item_is_set():
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
