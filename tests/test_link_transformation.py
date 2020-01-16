from tests.helpers import add_component_to_file
from PySide2.QtGui import QVector3D
from nexus_constructor.component.component import Component


def test_linked_component_is_none_1(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    assert component1.transforms.link.linked_component is None


def test_linked_component_is_none_2(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    component1.transforms.has_link = False
    assert component1.transforms.link.linked_component is None


def test_linked_component_is_none_3(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    new_component = Component(component1.file, component1.group)
    assert new_component.transforms.link.linked_component is None


def test_linked_component_via_transform_1(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    rot = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component2.depends_on = rot
    component1.depends_on = rot

    new_component = Component(component1.file, component1.group)
    assert new_component.transforms.link.linked_component == component2


def test_linked_component_via_transform_2(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot1
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    rot2 = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component2.depends_on = rot2
    rot1.depends_on = rot2

    new_component = Component(component1.file, component1.group)
    assert new_component.transforms.link.linked_component == component2


def test_linked_component_via_component_1(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    rot = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component2.depends_on = rot
    component1.transforms.link.linked_component = component2

    new_component = Component(component1.file, component1.group)
    assert new_component.transforms.link.linked_component == component2


def test_linked_component_via_component_2(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot1
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    rot2 = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component2.depends_on = rot2
    component1.transforms.link.linked_component = component2

    new_component = Component(component1.file, component1.group)
    assert new_component.transforms.link.linked_component == component2
