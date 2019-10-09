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


def create_transform(nexus_file, name):
    initial_value = 42
    initial_vector = QVector3D(1.0, 0.0, 0.0)
    initial_type = "Translation"
    dataset = _add_transform_to_file(
        nexus_file, name, initial_value, initial_vector, initial_type
    )
    return Transformation(nexus_file, dataset)


def test_can_set_transform_properties():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    initial_name = "slartibartfast"

    transform = create_transform(nexus_wrapper, initial_name)

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


def test_set_one_dependent():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform1 = create_transform(nexus_wrapper, "transform_1")

    transform2 = create_transform(nexus_wrapper, "transform_2")

    transform1.register_dependent(transform2)

    set_dependents = transform1.get_dependents()

    assert len(set_dependents) == 1
    assert set_dependents[0] == transform2


def test_set_two_dependents():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform1 = create_transform(nexus_wrapper, "transform_1")

    transform2 = create_transform(nexus_wrapper, "transform_2")

    transform3 = create_transform(nexus_wrapper, "transform_3")

    transform1.register_dependent(transform2)
    transform1.register_dependent(transform3)

    set_dependents = transform1.get_dependents()

    assert len(set_dependents) == 2
    assert set_dependents[0] == transform2
    assert set_dependents[1] == transform3


def test_set_three_dependents():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform1 = create_transform(nexus_wrapper, "transform_1")

    transform2 = create_transform(nexus_wrapper, "transform_2")

    transform3 = create_transform(nexus_wrapper, "transform_3")

    transform4 = create_transform(nexus_wrapper, "transform_4")

    transform1.register_dependent(transform2)
    transform1.register_dependent(transform3)
    transform1.register_dependent(transform4)

    set_dependents = transform1.get_dependents()

    assert len(set_dependents) == 3
    assert set_dependents[0] == transform2
    assert set_dependents[1] == transform3
    assert set_dependents[2] == transform4


def test_deregister_dependent():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform1 = create_transform(nexus_wrapper, "transform_1")

    transform2 = create_transform(nexus_wrapper, "transform_2")

    transform1.register_dependent(transform2)
    transform1.deregister_dependent(transform2)

    set_dependents = transform1.get_dependents()

    assert set_dependents == None


def test_deregister_unregistered_dependent_alt1():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform1 = create_transform(nexus_wrapper, "transform_1")
    transform2 = create_transform(nexus_wrapper, "transform_2")

    transform1.deregister_dependent(transform2)

    assert transform1.get_dependents() == None


def test_deregister_unregistered_dependent_alt2():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform1 = create_transform(nexus_wrapper, "transform_1")
    transform2 = create_transform(nexus_wrapper, "transform_2")
    transform3 = create_transform(nexus_wrapper, "transform_3")

    transform1.register_dependent(transform3)
    transform1.deregister_dependent(transform2)

    assert len(transform1.get_dependents()) == 1
    assert transform1.get_dependents()[0] == transform3


def test_deregister_unregistered_dependent_alt3():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform1 = create_transform(nexus_wrapper, "transform_1")
    transform2 = create_transform(nexus_wrapper, "transform_2")
    transform3 = create_transform(nexus_wrapper, "transform_2_alt")
    transform4 = create_transform(nexus_wrapper, "transform_3")

    transform1.register_dependent(transform3)
    transform1.register_dependent(transform4)
    transform1.deregister_dependent(transform2)

    assert len(transform1.get_dependents()) == 2
    assert transform1.get_dependents()[0] == transform3
    assert transform1.get_dependents()[1] == transform4


def test_reregister_dependent():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform1 = create_transform(nexus_wrapper, "transform_1")

    transform2 = create_transform(nexus_wrapper, "transform_2")

    transform3 = create_transform(nexus_wrapper, "transform_3")

    transform1.register_dependent(transform2)
    transform1.deregister_dependent(transform2)
    transform1.register_dependent(transform3)

    set_dependents = transform1.get_dependents()

    assert len(set_dependents) == 1
    assert set_dependents[0] == transform3


from tests.helpers import add_component_to_file


def test_set_one_dependent_component():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform = create_transform(nexus_wrapper, "transform_1")

    component = add_component_to_file(nexus_wrapper, "test_component")

    transform.register_dependent(component)

    set_dependents = transform.get_dependents()

    assert len(set_dependents) == 1
    assert set_dependents[0] == component


def test_set_two_dependent_components():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform = create_transform(nexus_wrapper, "transform_1")

    component1 = add_component_to_file(nexus_wrapper, component_name="test_component1")
    component2 = add_component_to_file(nexus_wrapper, component_name="test_component2")

    transform.register_dependent(component1)
    transform.register_dependent(component2)

    set_dependents = transform.get_dependents()

    assert len(set_dependents) == 2
    assert set_dependents[0] == component1
    assert set_dependents[1] == component2


def test_set_three_dependent_components():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform = create_transform(nexus_wrapper, "transform_1")

    component1 = add_component_to_file(nexus_wrapper, component_name="test_component1")
    component2 = add_component_to_file(nexus_wrapper, component_name="test_component2")
    component3 = add_component_to_file(nexus_wrapper, component_name="test_component3")

    transform.register_dependent(component1)
    transform.register_dependent(component2)
    transform.register_dependent(component3)

    set_dependents = transform.get_dependents()

    assert len(set_dependents) == 3
    assert set_dependents[0] == component1
    assert set_dependents[1] == component2
    assert set_dependents[2] == component3


def test_deregister_three_dependent_components():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform = create_transform(nexus_wrapper, "transform_1")

    component1 = add_component_to_file(nexus_wrapper, component_name="test_component1")
    component2 = add_component_to_file(nexus_wrapper, component_name="test_component2")
    component3 = add_component_to_file(nexus_wrapper, component_name="test_component3")

    transform.register_dependent(component1)
    transform.register_dependent(component2)
    transform.register_dependent(component3)

    transform.deregister_dependent(component1)
    transform.deregister_dependent(component2)
    transform.deregister_dependent(component3)

    set_dependents = transform.get_dependents()

    assert len(set_dependents) == 0


def test_register_dependent_twice():
    nexus_wrapper = NexusWrapper(str(uuid1()))

    transform = create_transform(nexus_wrapper, "transform_1")

    component1 = add_component_to_file(nexus_wrapper, component_name="test_component1")

    transform.register_dependent(component1)
    transform.register_dependent(component1)

    set_dependents = transform.get_dependents()

    assert len(set_dependents) == 1
