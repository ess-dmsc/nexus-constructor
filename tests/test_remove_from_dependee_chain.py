from tests.helpers import add_component_to_file
from PySide2.QtGui import QVector3D


def test_remove_from_beginning_1(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot
    assert len(rot.get_dependents()) == 1
    rot.remove_from_dependee_chain()
    assert component1.depends_on.absolute_path == "/"


def test_remove_from_beginning_2(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    rot2 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot1
    rot1.depends_on = rot2
    assert len(rot2.get_dependents()) == 1
    rot1.remove_from_dependee_chain()
    assert len(rot2.get_dependents()) == 1
    assert rot2.get_dependents()[0] == component1
    assert component1.depends_on == rot2


def test_remove_from_beginning_3(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    rot1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    rot2 = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot1
    component2.depends_on = rot2
    rot1.depends_on = rot2
    assert len(rot2.get_dependents()) == 2
    rot1.remove_from_dependee_chain()
    assert len(rot2.get_dependents()) == 2
    assert component2 in rot2.get_dependents()
    assert component1 in rot2.get_dependents()
    assert component1.depends_on == rot2
    assert component1.transforms.link.linked_component == component2


def test_remove_from_middle(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    component3 = add_component_to_file(nexus_wrapper, "field", 42, "component3")
    rot1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    rot2 = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    rot3 = component3.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot1
    component2.depends_on = rot2
    component3.depends_on = rot3
    component1.transforms.link.linked_component = component2
    component2.transforms.link.linked_component = component3
    rot2.remove_from_dependee_chain()
    assert rot1.depends_on == rot3
    assert component1.transforms.link.linked_component == component3
    assert rot1 in rot3.get_dependents()
    assert component3 in rot3.get_dependents()
