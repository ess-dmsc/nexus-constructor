from nexus_constructor.qml_models.helpers import change_value, generate_unique_name
from nexus_constructor.data_model import Component, ComponentType


def test_GIVEN_different_attribute_WHEN_change_value_called_THEN_changes_attribute_to_new_value():
    item = Component(ComponentType.SAMPLE, name="test")
    change_value(item, "name", "hello")
    assert item.name == "hello"


def test_GIVEN_same_value_WHEN_change_value_called_THEN_does_not_change_attribute():
    item = Component(ComponentType.SAMPLE, name="test")
    change_value(item, "name", "test")
    assert item.name == "test"


def test_GIVEN_nonexistent_attr_WHEN_change_value_called_THEN_does_nothing():
    item = Component(ComponentType.SAMPLE, name="test")
    attribute_that_shouldnt_exist = "somethingthatdoesntexist"
    change_value(item, attribute_that_shouldnt_exist, "test")
    try:
        getattr(item, attribute_that_shouldnt_exist)
        assert False
    except AttributeError:
        assert True


base = "component"


def test_GIVEN_empty_list_WHEN_generating_unique_name_THEN_returns_base_name():
    assert base == generate_unique_name(base, [])


def test_GIVEN_list_with_existing_component_WHEN_generating_unique_name_THEN_increments_value_on_end():
    components = [Component(ComponentType.SAMPLE, name=base)]
    assert (base + "1") == generate_unique_name(base, components)


def test_GIVEN_list_with_base_and_unique_name_from_base_WHEN_generating_unique_name_THEN_generates_something_different():
    components = [
        Component(ComponentType.SAMPLE, name=base),
        Component(ComponentType.SAMPLE, name=(base + "1")),
    ]
    assert (base + "2") == generate_unique_name(base, components)


def test_GIVEN_list_without_base_WHEN_generating_unique_name_THEN_generates_base():
    components = [Component(ComponentType.SAMPLE, name=(base + "1"))]
    assert base == generate_unique_name(base, components)


def test_GIVEN_base_with_number_on_end_WHEN_generating_unique_name_THEN_does_not_increment_number():
    base_num = "component1"
    components = [Component(ComponentType.SAMPLE, name=(base_num))]
    assert base_num + "1" == generate_unique_name(base_num, components)
