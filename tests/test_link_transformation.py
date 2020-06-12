from tests.helpers import add_component_to_file


def test_linked_component_is_none_1():
    component1 = add_component_to_file("field", 42, "component1")
    assert component1.transforms.link.linked_component is None


def test_linked_component_is_none_2():
    component1 = add_component_to_file("field", 42, "component1")
    component1.transforms.has_link = False
    assert component1.transforms.link.linked_component is None
