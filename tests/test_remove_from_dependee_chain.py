import pytest
from PySide2.QtGui import QVector3D

from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.module import Dataset
from nexus_constructor.model.value_type import ValueTypes

values = Dataset(
    name="scalar_value",
    type=ValueTypes.DOUBLE,
    values=90.0,
    parent_node=None,
)


@pytest.fixture
def instrument():
    return Entry(parent_node=None)


@pytest.mark.skip(reason="old model used")
def test_remove_from_beginning_1(instrument):
    component1 = Component("component1", instrument)
    rot = component1.add_rotation(
        name="rotation1",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
    )
    component1.depends_on = rot
    assert len(rot.dependents) == 1
    rot.remove_from_dependee_chain()
    assert component1.depends_on is None


@pytest.mark.skip(reason="old model used")
def test_remove_from_beginning_2(instrument):
    component1 = Component("component1", instrument)
    rot1 = component1.add_rotation(
        name="rotation1",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
    )
    rot2 = component1.add_rotation(
        name="rotation2",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
    )
    component1.depends_on = rot1
    rot1.depends_on = rot2
    assert len(rot2.dependents) == 1
    rot1.remove_from_dependee_chain()
    assert len(rot2.dependents) == 1
    assert rot2.dependents[0] == component1
    assert component1.depends_on == rot2


@pytest.mark.skip(reason="old model used")
def test_remove_from_beginning_3(instrument):
    component1 = Component("component1", instrument)
    component2 = Component("component2", instrument)
    rot1 = component1.add_rotation(
        name="rotation1",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
    )
    rot2 = component2.add_rotation(
        name="rotation2",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
    )
    component1.depends_on = rot1
    component2.depends_on = rot2
    rot1.depends_on = rot2
    assert len(rot2.dependents) == 2
    rot1.remove_from_dependee_chain()
    assert len(rot2.dependents) == 2
    assert component2 in rot2.dependents
    assert component1 in rot2.dependents
    assert component1.depends_on == rot2
    assert component1.transforms.link.linked_component == component2


def test_remove_from_middle():
    component1 = Component("component1", instrument)
    component2 = Component("component2", instrument)
    component3 = Component("component3", instrument)
    rot1 = component1.add_rotation(
        name="rotation1",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
    )
    rot2 = component2.add_rotation(
        name="rotation2",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
    )
    rot3 = component3.add_rotation(
        name="rotation3",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
    )
    component1.depends_on = rot1
    component2.depends_on = rot2
    component3.depends_on = rot3

    component1.transforms.link.linked_component = component2
    component2.transforms.link.linked_component = component3
    rot2.remove_from_dependee_chain()
    assert rot1.depends_on == rot3
    assert component1.transforms.link.linked_component == component3
    assert rot1 in rot3.dependents
    assert component3 in rot3.dependents


def test_remove_from_end():
    component1 = Component("component1", instrument)
    rot1 = component1.add_rotation(
        name="rotation1",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
    )
    rot2 = component1.add_rotation(
        name="rotation2",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
        depends_on=rot1,
    )
    rot3 = component1.add_rotation(
        name="rotation3",
        axis=QVector3D(1.0, 0.0, 0.0),
        angle=values.values,
        values=values,
        depends_on=rot2,
    )

    component1.depends_on = rot3

    rot1.remove_from_dependee_chain()

    assert rot1.depends_on is None
    assert not rot1.dependents

    assert component1.depends_on == rot3

    assert rot2.dependents[0] == rot3
    assert len(component1.transforms) == 2
