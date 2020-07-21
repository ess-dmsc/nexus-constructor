from nexus_constructor.model.component import Component
from nexus_constructor.model.node import _get_item, _remove_item, _set_item, Node


def test_get_item_returns_correct_component_when_given_component_is_in_list():
    name = "component1"
    test = Component(name)

    list_of_components = [test]
    assert _get_item(list_of_components, name) == test


def test_get_item_throws_error_when_component_is_not_in_list_then_works_when_item_is_set():
    name = "component1"
    test = Component(name)

    list_of_components = []

    assert _get_item(list_of_components, name) is None

    _set_item(None, list_of_components, name, test)
    assert _get_item(list_of_components, name) == test


def test_remove_item_removes_item_from_list():
    name = "component1"
    test = Component(name)

    list_of_components = [test]

    _remove_item(list_of_components, name)

    assert not list_of_components


def test_remove_item_removes_single_item_in_list_and_not_everything():
    comp1_name = "component1"
    comp1 = Component(comp1_name)

    comp2_name = "component2"
    comp2 = Component(comp2_name)

    list_of_components = [comp1, comp2]
    _remove_item(list_of_components, comp1_name)

    assert list_of_components == [comp2]


def test_set_item_works_on_list_that_has_components_in():
    comp1_name = "component1"
    comp1 = Component(comp1_name)

    list_of_components = [comp1]

    comp2_name = "component2"
    comp2 = Component(comp2_name)

    _set_item(None, list_of_components, comp2_name, comp2)

    assert list_of_components == [comp1, comp2]


def test_set_item_with_existing_component_in_overwrites_if_name_is_same():
    comp1_name = "component1"
    comp1 = Component(comp1_name)

    comp2 = Component(comp1_name)
    nx_class = "NXaperture"
    comp2.nx_class = nx_class

    list_of_components = [comp1]

    _set_item(None, list_of_components, comp1_name, comp2)

    assert list_of_components[0].nx_class == nx_class


def test_get_absolute_path_works_with_no_parent():
    name = "test"
    node = Node(name=name, parent_node=None)

    assert node.absolute_path == f"/{name}"


def test_get_absolute_path_works_if_component_with_parents():
    name1 = "thing1"
    node1 = Node(name=name1, parent_node=None)
    name2 = "thing2"
    node2 = Node(name=name2, parent_node=node1)
    assert node2.absolute_path == f"/{name1}/{name2}"
