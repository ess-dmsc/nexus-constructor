from PySide2.QtGui import QVector3D

from nexus_constructor.model.component import Component
from nexus_constructor.model.module import Dataset
from nexus_constructor.model.value_type import ValueTypes


def test_new_component_returns_none_as_linked_component():
    component = Component(name="test_component")
    assert component.transforms.link.linked_component is None


def test_end_of_depends_on_chain_of_component_is_linked_to_other_component():
    # GIVEN component has depends_on chain with multiple transformations
    component = Component(name="test_component")
    values = Dataset(parent_node=None, name="", type=ValueTypes.INT, values=[42])
    transforms_2 = component.add_translation(
        name="transform2",
        vector=QVector3D(0, 0, 1.0),  # default to beam direction
        values=values,
    )
    transform_1 = component.add_translation(
        name="transform1",
        vector=QVector3D(0, 0, 1.0),  # default to beam direction
        values=values,
        depends_on=transforms_2,
    )
    component.depends_on = transform_1

    # WHEN it is linked to another component
    another_component = Component(name="another_test_component")
    transform_3 = another_component.add_translation(
        name="transform3",
        vector=QVector3D(0, 0, 1.0),  # default to beam direction
        values=values,
    )
    another_component.depends_on = transform_3
    component.transforms.link.linked_component = another_component

    # THEN it is the last component of the depends_on chain which has its depends_on property updated
    assert transforms_2.depends_on == transform_3
