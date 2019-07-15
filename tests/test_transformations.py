from nexus_constructor.transformations import Transformation, QVector3D
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from typing import Any
from nexus_constructor.ui_utils import qvector3d_to_numpy_array
from uuid import uuid1

transform_type = "Transformation"
rotation_type = "Rotation"
translation_type = "Translation"


def _add_transform_to_file(
    nexus_wrapper: NexusWrapper,
    name: str,
    value: Any,
    vector: QVector3D,
    transform_type: str,
):
    transform_dataset = nexus_wrapper.nexus_file.create_dataset(name, data=value)
    transform_dataset.attrs["vector"] = qvector3d_to_numpy_array(vector)
    transform_dataset.attrs["transformation_type"] = transform_type
    return transform_dataset


def test_can_get_transform_properties():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    test_name = "slartibartfast"
    test_value = 42
    test_vector = QVector3D(1.0, 0.0, 0.0)
    test_type = "Translation"

    transform_dataset = _add_transform_to_file(
        nexus_wrapper, test_name, test_value, test_vector, test_type
    )

    transform = Transformation(nexus_wrapper, transform_dataset)

    assert (
        transform.name == test_name
    ), "Expected the transform name to match what was in the NeXus file"
    assert (
        transform.value == test_value
    ), "Expected the transform value to match what was in the NeXus file"
    assert (
        transform.vector == test_vector
    ), "Expected the transform vector to match what was in the NeXus file"
    assert (
        transform.type == test_type
    ), "Expected the transform type to match what was in the NeXus file"


def test_can_set_transform_properties():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    initial_name = "slartibartfast"
    initial_value = 42
    initial_vector = QVector3D(1.0, 0.0, 0.0)
    initial_type = "Translation"

    transform_dataset = _add_transform_to_file(
        nexus_wrapper, initial_name, initial_value, initial_vector, initial_type
    )

    transform = Transformation(nexus_wrapper, transform_dataset)

    test_name = "beeblebrox"
    test_value = 34
    test_vector = QVector3D(0.0, 0.0, 1.0)
    test_type = "Rotation"

    transform.name = test_name
    transform.value = test_value
    transform.vector = test_vector
    transform.type = test_type

    assert (
        transform.name == test_name
    ), "Expected the transform name to match what was in the NeXus file"
    assert (
        transform.value == test_value
    ), "Expected the transform value to match what was in the NeXus file"
    assert (
        transform.vector == test_vector
    ), "Expected the transform vector to match what was in the NeXus file"
    assert (
        transform.type == test_type
    ), "Expected the transform type to match what was in the NeXus file"
