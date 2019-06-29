from nexus_constructor.component import ComponentModel, DependencyError
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from cmath import isclose
from typing import Any
from PySide2.QtGui import QVector3D
import pytest
from uuid import uuid1


def _add_component_to_file(
    nexus_wrapper: NexusWrapper,
    field_name: str,
    field_value: Any,
    component_name: str = "test_component",
):
    component_group = nexus_wrapper.nexus_file.create_group(component_name)
    component_group.create_dataset(field_name, data=field_value)
    return component_group


def test_can_create_and_read_from_field_in_component():
    field_name = "some_field"
    field_value = 42
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(nexus_wrapper, field_name, field_value)
    component = ComponentModel(nexus_wrapper, component_group)
    returned_value = component.get_field(field_name)
    assert (
        returned_value == field_value
    ), "Expected to get same value back from field as it was created with"


def test_nameerror_raised_if_requested_field_does_not_exist():
    field_name = "some_field"
    field_value = 42
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(nexus_wrapper, field_name, field_value)
    component = ComponentModel(nexus_wrapper, component_group)
    try:
        component.get_field("nonexistent_field")
    except NameError:
        pass  # as expected


def test_created_component_has_specified_name():
    name = "component_name"
    field_name = "some_field"
    field_value = 42
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, field_name, field_value, name
    )
    component = ComponentModel(nexus_wrapper, component_group)
    assert component.name == name


def test_component_can_be_renamed():
    initial_name = "component_name"
    field_name = "some_field"
    field_value = 42
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, field_name, field_value, initial_name
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
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, field_name, initial_value, name
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
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, field_name, initial_value, name
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


def test_GIVEN_new_component_WHEN_get_transforms_for_component_THEN_transforms_list_is_empty():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component = ComponentModel(nexus_wrapper, component_group)
    assert (
        len(component.transforms_full_chain) == 0
    ), "expected there to be no transformations in the newly created component"


def test_GIVEN_component_with_a_transform_added_WHEN_get_transforms_for_component_THEN_transforms_list_contains_transform():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component = ComponentModel(nexus_wrapper, component_group)

    transform = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = transform

    assert (
        len(component.transforms_full_chain) == 1
    ), "expected there to be a transformation in the component"


def test_GIVEN_component_with_a_transform_added_WHEN_transform_is_deleted_THEN_transforms_list_is_empty():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component = ComponentModel(nexus_wrapper, component_group)

    transform = component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)

    component.remove_transformation(transform)

    assert (
        len(component.transforms_full_chain) == 0
    ), "expected there to be no transforms in the component"


def test_GIVEN_a_component_with_a_transform_dependency_WHEN_get_depends_on_THEN_transform_dependency_is_returned():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component = ComponentModel(nexus_wrapper, component_group)

    input_transform = component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component.depends_on = input_transform

    returned_transform = component.depends_on

    assert returned_transform.dataset.name == input_transform.dataset.name


def test_deleting_a_transformation_from_a_different_component_is_not_allowed():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    first_component = ComponentModel(nexus_wrapper, component_group)
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )
    second_component = ComponentModel(nexus_wrapper, component_group)

    transform = first_component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)

    with pytest.raises(PermissionError):
        assert second_component.remove_transformation(
            transform
        ), "Expected not to be allowed to delete the transform as it belongs to a different component"


def test_deleting_a_transformation_which_the_component_directly_depends_on_is_not_allowed():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component = ComponentModel(nexus_wrapper, component_group)
    transform = component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component.depends_on = transform

    with pytest.raises(DependencyError):
        assert component.remove_transformation(
            transform
        ), "Expected not to be allowed to delete the transform as the component directly depends on it"


def test_deleting_a_transformation_which_the_component_indirectly_depends_on_is_not_allowed():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component = ComponentModel(nexus_wrapper, component_group)
    first_transform = component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    second_transform = component.add_translation(
        QVector3D(1.0, 0.0, 0.0), depends_on=first_transform
    )
    component.depends_on = second_transform

    with pytest.raises(DependencyError):
        assert component.remove_transformation(
            first_transform
        ), "Expected not to be allowed to delete the transform as the component indirectly depends on it"


def test_transforms_contains_only_local_transforms_not_full_depends_on_chain():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    first_component = ComponentModel(nexus_wrapper, component_group)
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )
    second_component = ComponentModel(nexus_wrapper, component_group)

    first_transform = first_component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    second_transform = second_component.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=first_transform
    )

    second_component.depends_on = second_transform

    assert len(
        second_component.transforms
    ), "Expect transforms list to contain only the 1 transform local to this component"


def test_removing_transformation_which_has_a_dependent_transform_in_another_component_is_not_allowed():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    first_component = ComponentModel(nexus_wrapper, component_group)
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )
    second_component = ComponentModel(nexus_wrapper, component_group)

    first_transform = first_component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    second_transform = second_component.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=first_transform
    )

    second_component.depends_on = second_transform

    with pytest.raises(DependencyError):
        assert first_component.remove_transformation(
            first_transform
        ), "Expected not to be allowed to delete the transform as a transform in another component depends on it"


def test_removing_transformation_which_no_longer_has_a_dependent_transform_in_another_component_is_allowed():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    first_component = ComponentModel(nexus_wrapper, component_group)
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )
    second_component = ComponentModel(nexus_wrapper, component_group)

    first_transform = first_component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    second_transform = second_component.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=first_transform
    )

    second_component.depends_on = second_transform

    # Make second transform no longer depend on the first
    second_transform.depends_on = None

    try:
        first_component.remove_transformation(first_transform)
    except Exception:
        pytest.fail(
            "Expected to be able to remove transformation which is no longer a dependee"
        )


def test_removing_transformation_which_still_has_one_dependent_transform_is_not_allowed():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component = ComponentModel(nexus_wrapper, component_group)

    first_transform = component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    second_transform = component.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=first_transform
    )
    third_transform = component.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=first_transform
    )

    # Make third transform no longer depend on the first one
    third_transform.depends_on = None

    with pytest.raises(DependencyError):
        assert component.remove_transformation(
            first_transform
        ), "Expected not to be allowed to delete the transform as the second transform still depends on it"
