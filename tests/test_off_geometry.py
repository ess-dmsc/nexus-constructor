from nexus_constructor.geometry import OFFGeometryNoNexus, OFFGeometryNexus
from PySide2.QtGui import QVector3D
from .helpers import create_nexus_wrapper, add_component_to_file
from pytest import approx


def test_GIVEN_nothing_WHEN_constructing_OFFGeometry_THEN_geometry_str_is_OFF():
    geom = OFFGeometryNoNexus()
    assert geom.geometry_str == "OFF"


UNIT = "m"
AXIS_DIRECTION = QVector3D(1, 2, 3)
HEIGHT = 2.0
RADIUS = 1.0


def test_GIVEN_faces_WHEN_calling_winding_order_on_OFF_THEN_order_is_correct():
    vertices = [
        QVector3D(0, 0, 1),
        QVector3D(0, 1, 0),
        QVector3D(0, 0, 0),
        QVector3D(0, 1, 1),
    ]

    faces = [[0, 1, 2, 3]]

    geom = OFFGeometryNoNexus(vertices, faces)
    expected = [point for face in faces for point in face]

    assert expected == geom.winding_order


def test_GIVEN_faces_WHEN_calling_winding_order_indices_on_OFF_THEN_order_is_correct():
    vertices = [
        QVector3D(0, 0, 1),
        QVector3D(0, 1, 0),
        QVector3D(0, 0, 0),
        QVector3D(0, 1, 1),
    ]

    faces = [[0, 1, 2, 3]]

    geom = OFFGeometryNoNexus(vertices, faces)

    expected = [0]  # only one face

    assert expected == geom.winding_order_indices


def test_GIVEN_off_geometry_WHEN_calling_off_geometry_on_offGeometry_THEN_original_geometry_is_returned():
    vertices = [
        QVector3D(0, 0, 1),
        QVector3D(0, 1, 0),
        QVector3D(0, 0, 0),
        QVector3D(0, 1, 1),
    ]

    faces = [[0, 1, 2, 3]]
    geom = OFFGeometryNoNexus(vertices, faces)

    assert geom.faces == faces
    assert geom.vertices == vertices
    assert geom.off_geometry == geom


def test_can_get_off_geometry_properties():
    nexus_wrapper = create_nexus_wrapper()
    component = add_component_to_file(nexus_wrapper)

    vertex_3_x = 0.0
    vertex_3_y = 1.0
    vertex_3_z = 1.0

    vertices = [
        QVector3D(0, 0, 1),
        QVector3D(0, 1, 0),
        QVector3D(0, 0, 0),
        QVector3D(vertex_3_x, vertex_3_y, vertex_3_z),
    ]

    faces = [[0, 1, 2, 3]]

    shape = OFFGeometryNoNexus(vertices, faces)

    component.set_off_shape(shape)

    nexus_shape = component.get_shape()
    assert isinstance(nexus_shape, OFFGeometryNexus)
    assert nexus_shape.faces == faces
    assert nexus_shape.vertices[3].x() == approx(vertex_3_x)
    assert nexus_shape.vertices[3].y() == approx(vertex_3_y)
    assert nexus_shape.vertices[3].z() == approx(vertex_3_z)


def test_can_set_off_geometry_properties():
    nexus_wrapper = create_nexus_wrapper()
    component = add_component_to_file(nexus_wrapper)

    vertices = [
        QVector3D(0.0, 0.0, 1.0),
        QVector3D(0.0, 1.0, 0.0),
        QVector3D(0.0, 0.0, 0.0),
        QVector3D(0.0, 1.0, 1.0),
    ]

    faces = [[0, 1, 2, 3]]

    shape = OFFGeometryNoNexus(vertices, faces)

    component.set_off_shape(shape)

    nexus_shape = component.get_shape()

    vertex_2_x = 0.5
    vertex_2_y = -0.5
    vertex_2_z = 0
    new_vertices = [
        QVector3D(-0.5, -0.5, 0),
        QVector3D(0, 0.5, 0),
        QVector3D(vertex_2_x, vertex_2_y, vertex_2_z),
    ]
    triangle = [0, 1, 2]
    new_faces = [triangle]
    nexus_shape.vertices = new_vertices
    nexus_shape.faces = new_faces

    assert nexus_shape.faces == new_faces
    assert nexus_shape.vertices[2].x() == approx(vertex_2_x)
    assert nexus_shape.vertices[2].y() == approx(vertex_2_y)
    assert nexus_shape.vertices[2].z() == approx(vertex_2_z)
