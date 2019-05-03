from nexus_constructor.qml_models.helpers import generate_unique_name
from nexus_constructor.component_type import ComponentType
from nexus_constructor.component import Component


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
