import numpy as np
from PySide2.QtGui import QVector3D

from nexus_constructor.common_attrs import CommonKeys, NodeType
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.group import Group
from nexus_constructor.model.stream import F142Stream, WriterModules
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.model.value_type import ValueTypes


def create_transform(
    name="test translation",
    ui_value=42.0,
    vector=QVector3D(1.0, 0.0, 0.0),
    type="translation",
    values=Dataset(name="", values=None, type=ValueTypes.DOUBLE),
):
    translation = Transformation(
        name=name,
        parent_node=None,
        values=values,
        type=ValueTypes.STRING,
        parent_component=None,
    )

    translation.vector = vector
    translation.transform_type = type
    translation.ui_value = ui_value

    return translation


def test_can_get_transform_properties():
    test_name = "slartibartfast"
    test_ui_value = 42
    test_vector = QVector3D(1.0, 0.0, 0.0)
    test_type = "translation"
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
        transform.transform_type == test_type
    ), "Expected the transform type to match what was in the NeXus file"
    assert (
        transform.values == test_values
    ), "Expected the transform type to match what was in the NeXus file"


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
    test_type = "rotation"
    test_values = Dataset("valuedataset", None, [1, 2])

    transform.name = test_name
    transform.ui_value = test_ui_value
    transform.vector = test_vector
    transform.transform_type = test_type
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
        transform.transform_type == test_type
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
    component = Component("test_component")
    transform.register_dependent(component)

    set_dependents = transform.dependents

    assert len(set_dependents) == 1
    assert set_dependents[0] == component


def test_set_two_dependent_components():
    transform = create_transform("transform_1")

    component1 = Component("component1")
    component2 = Component("component2")

    transform.register_dependent(component1)
    transform.register_dependent(component2)

    set_dependents = transform.dependents

    assert len(set_dependents) == 2
    assert set_dependents[0] == component1
    assert set_dependents[1] == component2


def test_set_three_dependent_components():
    transform = create_transform("transform_1")

    component1 = Component("test_component1")
    component2 = Component("test_component2")
    component3 = Component("test_component3")

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

    component1 = Component("test_component1")
    component2 = Component("test_component2")
    component3 = Component("test_component3")

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
    component1 = Component("test_component1")

    transform.register_dependent(component1)
    transform.register_dependent(component1)

    set_dependents = transform.dependents

    assert len(set_dependents) == 1


def test_can_get_translation_as_4_by_4_matrix():
    test_ui_value = 42.0
    # Note, it should not matter if this is not set to a unit vector
    test_vector = QVector3D(2.0, 0.0, 0.0)
    test_type = "translation"

    transformation = create_transform(
        ui_value=test_ui_value, vector=test_vector, type=test_type
    )

    test_matrix = transformation.qmatrix
    # NB, -1 * distance because the transformation in the UI is a passive transformation
    expected_matrix = np.array(
        (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -1 * test_ui_value, 0, 0, 1)
    )
    assert np.allclose(expected_matrix, np.array(test_matrix.data()))


def test_can_get_rotation_as_4_by_4_matrix():
    test_ui_value = 15.0  # degrees
    test_vector = QVector3D(0.0, 1.0, 0.0)  # around y-axis
    test_type = "rotation"

    transformation = create_transform(
        ui_value=test_ui_value, vector=test_vector, type=test_type
    )

    test_matrix = transformation.qmatrix
    # for a rotation around the y-axis:
    test_value_radians = np.deg2rad(test_ui_value)
    expected_matrix = np.array(
        (
            np.cos(test_value_radians),
            0,
            np.sin(test_value_radians),
            0,
            0,
            1,
            0,
            0,
            -np.sin(test_value_radians),
            0,
            np.cos(test_value_radians),
            0,
            0,
            0,
            0,
            1,
        )
    )
    assert np.allclose(expected_matrix, np.array(test_matrix.data()), atol=1.0e-7)


def test_GIVEN_transformation_with_scalar_value_that_is_not_castable_to_int_WHEN_getting_ui_value_THEN_ui_placeholder_value_is_returned_instead():
    transform_name = "transform_1"
    transform = create_transform(transform_name)

    str_value = "sdfji"
    transform.ui_value = str_value

    assert transform.ui_value != str_value
    assert transform.ui_value == 0


def test_as_dict_method_of_transformation_when_values_is_a_dataset():
    name = ":: SOME NAME ::"
    dataset = Dataset(name="", values=None, type=ValueTypes.DOUBLE)
    transform = create_transform(name=name, values=dataset)
    assert transform.values == dataset
    return_dict = transform.as_dict([])
    assert return_dict[CommonKeys.MODULE] == "dataset"
    assert return_dict[NodeType.CONFIG][CommonKeys.NAME] == name


def test_as_dict_method_of_transformation_when_values_is_a_f142_streamgroup():
    name = ":: SOME NAME ::"
    source = ":: SOME SOURCE ::"
    topic = (":: SOME TOPIC ::",)
    stream_group = Group(name="")
    stream_group.children = [
        F142Stream(parent_node=stream_group, source=source, topic=topic, type="double")
    ]
    transform = create_transform(name=name, values=stream_group)
    assert transform.values == stream_group

    return_dict = transform.as_dict([])
    print(return_dict)
    assert return_dict[CommonKeys.MODULE] == WriterModules.F142.value
    assert return_dict[NodeType.CONFIG][CommonKeys.NAME] == name
    assert return_dict[NodeType.CONFIG]["source"] == source
    assert return_dict[NodeType.CONFIG]["topic"] == topic


def test_if_scalar_and_invalid_value_entered_then_converting_to_dict_appends_error():
    transform = create_transform(
        values=Dataset(name="", values="not a number", type="double"),
        type=ValueTypes.DOUBLE,
    )

    error_collector = []
    transform.as_dict(error_collector)

    assert error_collector


def test_if_valid_value_entered_then_converting_to_dict_appends_no_error():
    transform = create_transform(
        values=Dataset(name="", values="123", type="double"),
        type=ValueTypes.DOUBLE,
    )

    error_collector = []
    transform.as_dict(error_collector)

    assert not error_collector
