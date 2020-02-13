from nexus_constructor.transformation_view import links_back_to_component
from tests.helpers import add_component_to_file
from PySide2.QtGui import QVector3D


def test_does_not_link_back_1(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")

    assert not links_back_to_component(component1, component2)


def test_does_not_link_back_2(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    translation1 = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component2.depends_on = translation1

    assert not links_back_to_component(component1, component2)


def test_does_not_link_back_3(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    component3 = add_component_to_file(nexus_wrapper, "field", 42, "component3")
    translation1 = component3.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component3.depends_on = translation1
    component2.transforms.link.linked_component = component3

    assert not links_back_to_component(component1, component2)


def test_does_not_link_back_4(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot2 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot2
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    component3 = add_component_to_file(nexus_wrapper, "field", 42, "component3")
    rot1 = component3.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component3.depends_on = rot1
    component2.transforms.link.linked_component = component3

    assert not links_back_to_component(component1, component2)


def test_links_back_1(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot2 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot2
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    component3 = add_component_to_file(nexus_wrapper, "field", 42, "component3")
    rot1 = component3.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component3.depends_on = rot1
    component2.transforms.link.linked_component = component3
    component3.transforms.link.linked_component = component1

    assert links_back_to_component(component1, component2)


def test_links_back_2(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")
    rot1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component1.depends_on = rot1
    component2 = add_component_to_file(nexus_wrapper, "field", 42, "component2")
    component2.transforms.link.linked_component = component1

    assert links_back_to_component(component1, component2)


def test_links_back_3(nexus_wrapper):
    component1 = add_component_to_file(nexus_wrapper, "field", 42, "component1")

    assert links_back_to_component(component1, component1)
