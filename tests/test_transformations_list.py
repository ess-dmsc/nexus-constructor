from tests.helpers import add_component_to_file
from PySide2.QtGui import QVector3D
from nexus_constructor.component.component import Component


def test_does_not_have_transformations_1(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    new_component = Component(component1.file, component1.group)
    assert len(new_component.transforms) == 0


def test_does_not_have_transformations_2(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    new_component = Component(component1.file, component1.group)
    assert len(new_component.transforms) == 0


def test_has_one_transformation_1(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot
    new_component = Component(component1.file, component1.group)
    assert len(new_component.transforms) == 1


def test_has_one_transformation_2(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot1
    new_component = Component(component1.file, component1.group)
    assert len(new_component.transforms) == 1


def test_has_two_transformations(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    rot2 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot1
    rot1.depends_on = rot2
    new_component = Component(component1.file, component1.group)
    assert len(new_component.transforms) == 2


def test_no_link_1(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    new_component = Component(component1.file, component1.group)
    assert not new_component.transforms.has_link


def test_no_link_2(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot
    new_component = Component(component1.file, component1.group)
    assert not new_component.transforms.has_link


def test_has_link_1(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    rot = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component2.depends_on = rot
    component1.transforms.link.linked_component = component2

    new_component = Component(component1.file, component1.group)
    assert new_component.transforms.has_link


def test_has_link_2(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot1
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    rot2 = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component2.depends_on = rot2
    rot1.depends_on = rot2

    new_component = Component(component1.file, component1.group)
    assert new_component.transforms.has_link
