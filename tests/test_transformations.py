import numpy as np
import pytest
from PySide2.QtGui import QVector3D

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset, DatasetMetadata
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.transformation_types import TransformationType
from typing import Any
from nexus_constructor.ui_utils import qvector3d_to_numpy_array
from tests.helpers import add_component_to_file  # noqa:F401

transform_type = "Transformation"
rotation_type = "Rotation"
translation_type = "Translation"


def _add_transform_to_file(
    name: str, value: Any, vector: QVector3D, transform_type: str
):
    transform = Transformation(name=name, dataset=DatasetMetadata(type=np.double))
    transform.type = transform_type
    transform.vector = vector
    transform.values = value

    return transform


def create_dataset():
    return Dataset("dataset", DatasetMetadata([1], str), "test")


@pytest.fixture
def dataset():
    return create_dataset()


def create_transform(
    name="test translation",
    ui_value=42.0,
    vector=QVector3D(1.0, 0.0, 0.0),
    type="Translation",
    values=Dataset("", None, []),
):

    translation = Transformation(name=name, dataset=dataset)

    translation.vector = vector
    translation.type = type
    translation.ui_value = ui_value
    translation.values = values

    return translation


def create_component(name=""):
    return Component(name=name, transforms_list=[])


def test_can_get_transform_properties(dataset):

    test_name = "slartibartfast"
    test_ui_value = 42
    test_vector = QVector3D(1.0, 0.0, 0.0)
    test_type = "Translation"
    test_values = Dataset("test_dataset", None, [1])

    transform = create_transform(
        name=test_name, vector=test_vector, ui_value=test_ui_value, values=test_values
    )

    assert (
        transform.name == test_name
    ), "Expected the transform name to match what was in the NeXus file"
    assert (
        transform.ui_value == test_ui_value
    ), "Expected the transform value to match what was in the NeXus file"
    assert (
        transform.vector == test_vector
    ), "Expected the transform vector to match what was in the NeXus file"
    assert (
        transform.type == test_type
    ), "Expected the transform type to match what was in the NeXus file"
    assert (
        transform.values == test_values
    ), "Expected the transform type to match what was in the NeXus file"


@pytest.mark.skip("Disabled whilst working on model change")
def test_transform_dependents_depends_on_are_updated_when_transformation_name_is_changed(
    nexus_wrapper,
):

    test_name = "slartibartfast"
    test_ui_value = 42
    test_vector = QVector3D(1.0, 0.0, 0.0)
    test_type = "Translation"

    transform_dataset = _add_transform_to_file(
        nexus_wrapper, test_name, test_ui_value, test_vector, test_type
    )

    component = nexus_wrapper.create_nx_group(
        "test", "NXaperture", nexus_wrapper.nexus_file
    )

    component = Component()

    component.create_dataset("depends_on", data=transform_dataset.name)

    transform = Transformation(nexus_wrapper, transform_dataset)
    transform.register_dependent(Component(nexus_wrapper, component))

    new_name = test_name + "1"

    transform.name = new_name

    assert transform.name == new_name
    assert str(component["depends_on"][()], encoding="UTF-8") == transform.dataset.name


@pytest.mark.skip("Disabled whilst working on model change")
@pytest.mark.parametrize("test_input", ["translation", "Translation", "TRANSLATION"])
def test_transform_type_is_capitalised(test_input, nexus_wrapper):
    test_name = "slartibartfast"
    test_ui_value = 42
    test_vector = QVector3D(1.0, 0.0, 0.0)
    transform_dataset = _add_transform_to_file(
        nexus_wrapper, test_name, test_ui_value, test_vector, test_input
    )
    transform = Transformation(nexus_wrapper, transform_dataset)
    assert transform.type == "Translation"


def test_ui_value_for_transform_with_array_magnitude_returns_first_value():
    transform_name = "transform1"
    array = [1.1, 2.2, 3.3]
    transform_ui_value = np.asarray(array, dtype=float)

    transformation = create_transform(name=transform_name, ui_value=transform_ui_value)

    assert transformation.ui_value == array[0]


def test_ui_value_for_transform_with_array_magnitude_of_strings_returns_zero():
    transform_name = "transform1"
    array = ["a1", "b1", "c1"]
    transform_ui_value = np.asarray(array)

    transformation = create_transform(name=transform_name, ui_value=transform_ui_value)
    assert transformation.ui_value == 0


def test_can_set_transform_properties():

    initial_name = "slartibartfast"

    transform = create_transform(initial_name)

    test_name = "beeblebrox"
    test_ui_value = 34.0
    test_vector = QVector3D(0.0, 0.0, 1.0)
    test_type = "Rotation"
    test_values = Dataset("valuedataset", None, [1, 2])

    transform.name = test_name
    transform.ui_value = test_ui_value
    transform.vector = test_vector
    transform.type = test_type
    transform.values = test_values

    assert (
        transform.name == test_name
    ), "Expected the transform name to match what was in the NeXus file"
    assert (
        transform.ui_value == test_ui_value
    ), "Expected the transform value to match what was in the NeXus file"
    assert (
        transform.vector == test_vector
    ), "Expected the transform vector to match what was in the NeXus file"
    assert (
        transform.type == test_type
    ), "Expected the transform type to match what was in the NeXus file"
    assert (
        transform.values == test_values
    ), "Expected the transform type to match what was in the NeXus file"


def test_set_one_dependent():

    transform1 = create_transform("transform_1")
    transform2 = create_transform("transform_2")

    transform1.register_dependent(transform2)

    set_dependents = transform1.dependents

    assert len(set_dependents) == 1
    assert set_dependents[0] == transform2


def test_set_two_dependents():

    transform1 = create_transform("transform_1")
    transform2 = create_transform("transform_2")
    transform3 = create_transform("transform_3")

    transform1.register_dependent(transform2)
    transform1.register_dependent(transform3)

    set_dependents = transform1.dependents

    assert len(set_dependents) == 2
    assert set_dependents[0] == transform2
    assert set_dependents[1] == transform3


def test_set_three_dependents():

    transform1 = create_transform("transform_1")
    transform2 = create_transform("transform_2")
    transform3 = create_transform("transform_3")
    transform4 = create_transform("transform_4")

    transform1.register_dependent(transform2)
    transform1.register_dependent(transform3)
    transform1.register_dependent(transform4)

    set_dependents = transform1.dependents

    assert len(set_dependents) == 3
    assert set_dependents[0] == transform2
    assert set_dependents[1] == transform3
    assert set_dependents[2] == transform4


def test_deregister_dependent():

    transform1 = create_transform("transform_1")
    transform2 = create_transform("transform_2")

    transform1.register_dependent(transform2)
    transform1.deregister_dependent(transform2)

    set_dependents = transform1.dependents

    assert not set_dependents


def test_deregister_unregistered_dependent_alt1():

    transform1 = create_transform("transform_1")
    transform2 = create_transform("transform_2")

    transform1.deregister_dependent(transform2)

    assert not transform1.dependents


def test_deregister_unregistered_dependent_alt2():

    transform1 = create_transform("transform_1")
    transform2 = create_transform("transform_2")
    transform3 = create_transform("transform_3")

    transform1.register_dependent(transform3)
    transform1.deregister_dependent(transform2)

    assert len(transform1.dependents) == 1
    assert transform1.dependents[0] == transform3


def test_deregister_unregistered_dependent_alt3():

    transform1 = create_transform("transform_1")
    transform2 = create_transform("transform_2")
    transform3 = create_transform("transform_2_alt")
    transform4 = create_transform("transform_3")

    transform1.register_dependent(transform3)
    transform1.register_dependent(transform4)
    transform1.deregister_dependent(transform2)

    assert len(transform1.dependents) == 2
    assert transform1.dependents[0] == transform3
    assert transform1.dependents[1] == transform4


def test_reregister_dependent():

    transform1 = create_transform("transform_1")
    transform2 = create_transform("transform_2")
    transform3 = create_transform("transform_3")

    transform1.register_dependent(transform2)
    transform1.deregister_dependent(transform2)
    transform1.register_dependent(transform3)

    set_dependents = transform1.dependents

    assert len(set_dependents) == 1
    assert set_dependents[0] == transform3


def test_set_one_dependent_component():

    transform = create_transform("transform_1")
    component = create_component()
    transform.register_dependent(component)

    set_dependents = transform.dependents

    assert len(set_dependents) == 1
    assert set_dependents[0] == component


def test_set_two_dependent_components():

    transform = create_transform("transform_1")

    component1 = create_component("component1")
    component2 = create_component("component2")

    transform.register_dependent(component1)
    transform.register_dependent(component2)

    set_dependents = transform.dependents

    assert len(set_dependents) == 2
    assert set_dependents[0] == component1
    assert set_dependents[1] == component2


def test_set_three_dependent_components():

    transform = create_transform("transform_1")

    component1 = create_component("test_component1")
    component2 = create_component("test_component2")
    component3 = create_component("test_component3")

    transform.register_dependent(component1)
    transform.register_dependent(component2)
    transform.register_dependent(component3)

    set_dependents = transform.dependents

    assert len(set_dependents) == 3
    assert set_dependents[0] == component1
    assert set_dependents[1] == component2
    assert set_dependents[2] == component3


def test_deregister_three_dependent_components():

    transform = create_transform("transform_1")

    component1 = create_component("test_component1")
    component2 = create_component("test_component2")
    component3 = create_component("test_component3")

    transform.register_dependent(component1)
    transform.register_dependent(component2)
    transform.register_dependent(component3)

    transform.deregister_dependent(component1)
    transform.deregister_dependent(component2)
    transform.deregister_dependent(component3)

    set_dependents = transform.dependents

    assert len(set_dependents) == 0


def test_register_dependent_twice():

    transform = create_transform("transform_1")
    component1 = create_component("test_component1")

    transform.register_dependent(component1)
    transform.register_dependent(component1)

    set_dependents = transform.dependents

    assert len(set_dependents) == 1


def test_can_get_translation_as_4_by_4_matrix():

    test_ui_value = 42.0
    # Note, it should not matter if this is not set to a unit vector
    test_vector = QVector3D(2.0, 0.0, 0.0)
    test_type = "Translation"

    transformation = create_transform(
        ui_value=test_ui_value, vector=test_vector, type=test_type
    )

    test_matrix = transformation.qmatrix
    expected_matrix = np.array(
        (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, test_ui_value, 0, 0, 1)
    )
    assert np.allclose(expected_matrix, np.array(test_matrix.data()))


def test_can_get_rotation_as_4_by_4_matrix():

    test_ui_value = 45.0  # degrees
    test_vector = QVector3D(0.0, 1.0, 0.0)  # around y-axis
    test_type = "Rotation"

    transformation = create_transform(
        ui_value=test_ui_value, vector=test_vector, type=test_type
    )

    test_matrix = transformation.qmatrix
    # for a rotation around the y-axis:
    test_value_radians = np.deg2rad(test_ui_value)
    expected_matrix = np.array(
        (
            np.cos(-test_value_radians),
            0,
            np.sin(-test_value_radians),
            0,
            0,
            1,
            0,
            0,
            -np.sin(-test_value_radians),
            0,
            np.cos(-test_value_radians),
            0,
            0,
            0,
            0,
            1,
        )
    )
    assert np.allclose(expected_matrix, np.array(test_matrix.data()), atol=1.0e-7)


@pytest.mark.skip("Disabled whilst working on model change")
def test_GIVEN_nexus_file_with_linked_transformation_but_without_dependee_of_attr_WHEN_opening_nexus_file_THEN_components_linked_contain_dependee_of_attribute(
    nexus_wrapper,
):
    transform_name = "transform_1"
    transform = create_transform(nexus_wrapper, transform_name)

    component1_name = "test_component1"
    component2_name = "test_component2"

    component1 = add_component_to_file(nexus_wrapper, component_name=component1_name)
    component2 = add_component_to_file(nexus_wrapper, component_name=component2_name)
    component1.depends_on = transform
    component2.depends_on = transform

    del transform._dataset.attrs[CommonAttrs.DEPENDEE_OF]

    nexus_wrapper.load_nexus_file(nexus_wrapper.nexus_file)
    new_transform_group = nexus_wrapper.nexus_file[transform_name]

    assert CommonAttrs.DEPENDEE_OF in new_transform_group.attrs
    assert len(new_transform_group.attrs[CommonAttrs.DEPENDEE_OF]) == 2
    assert (
        new_transform_group.attrs[CommonAttrs.DEPENDEE_OF][0] == "/" + component1_name
    )
    assert (
        new_transform_group.attrs[CommonAttrs.DEPENDEE_OF][1] == "/" + component2_name
    )


@pytest.mark.skip("Disabled whilst working on model change")
def test_GIVEN_nexus_file_with_linked_transformation_but_without_dependee_of_attr_WHEN_opening_nexus_file_THEN_component_linked_contains_dependee_of_attribute(
    nexus_wrapper,
):
    transform_name = "transform_1"
    transform = create_transform(nexus_wrapper, transform_name)

    component1_name = "test_component1"

    component1 = add_component_to_file(nexus_wrapper, component_name=component1_name)
    component1.depends_on = transform
    del transform._dataset.attrs[CommonAttrs.DEPENDEE_OF]

    nexus_wrapper.load_nexus_file(nexus_wrapper.nexus_file)
    new_transform_group = nexus_wrapper.nexus_file[transform_name]

    assert CommonAttrs.DEPENDEE_OF in new_transform_group.attrs
    assert new_transform_group.attrs[CommonAttrs.DEPENDEE_OF] == "/" + component1_name


def test_GIVEN_transformation_with_scalar_value_that_is_not_castable_to_int_WHEN_getting_ui_value_THEN_ui_placeholder_value_is_returned_instead():
    transform_name = "transform_1"
    transform = create_transform(transform_name)

    str_value = "sdfji"
    transform.ui_value = str_value

    assert transform.ui_value != str_value
    assert transform.ui_value == 0


@pytest.mark.skip("Disabled whilst working on model change")
def test_multiple_relative_transform_paths_are_converted_to_absolute_path_in_dependee_of_field(
    file, nexus_wrapper
):
    component_name = "component_1"

    component1 = add_component_to_file(nexus_wrapper, component_name=component_name)
    # make depends_on point to relative transformations group
    component1.group["depends_on"] = "transformations/transform1"

    transformations_group = component1.group.create_group("transformations")

    transform1_name = "transform1"
    transform1_dataset = transformations_group.create_dataset(transform1_name, data=1)
    transform1_dataset.attrs[CommonAttrs.VECTOR] = qvector3d_to_numpy_array(
        QVector3D(1, 0, 0)
    )
    transform1_dataset.attrs[
        CommonAttrs.TRANSFORMATION_TYPE
    ] = TransformationType.TRANSLATION

    transform2_name = "transform2"

    # make transform1 depends_on point to relative transform in same directory
    transform1_dataset.attrs["depends_on"] = transform2_name

    transform2_dataset = transformations_group.create_dataset(transform2_name, data=2)
    transform2_dataset.attrs[CommonAttrs.VECTOR] = qvector3d_to_numpy_array(
        QVector3D(1, 1, 0)
    )
    transform2_dataset.attrs[
        CommonAttrs.TRANSFORMATION_TYPE
    ] = TransformationType.TRANSLATION

    # make sure the depends_on points to the absolute path of the transform it depends on in the file
    assert (
        Transformation(nexus_wrapper, transform1_dataset).depends_on.dataset.name
        == transform2_dataset.name
    )


@pytest.mark.skip("Disabled whilst working on model change")
def test_transforms_with_no_dependees_return_None_for_depends_on(nexus_wrapper):

    component_name = "component_1"

    component1 = add_component_to_file(nexus_wrapper, component_name=component_name)
    # make depends_on point to relative transformations group
    component1.group["depends_on"] = "transformations/transform1"

    transformations_group = component1.group.create_group("transformations")

    transform1_name = "transform1"
    transform1_dataset = transformations_group.create_dataset(transform1_name, data=1)
    transform1_dataset.attrs[CommonAttrs.VECTOR] = qvector3d_to_numpy_array(
        QVector3D(1, 0, 0)
    )
    transform1_dataset.attrs[
        CommonAttrs.TRANSFORMATION_TYPE
    ] = TransformationType.TRANSLATION

    transform1_dataset.attrs["depends_on"] = "."
    transformation = Transformation(nexus_wrapper, transform1_dataset)

    assert not transformation.depends_on
