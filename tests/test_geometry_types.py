from nexus_constructor.geometry import NoShapeGeometry, OFFGeometryNoNexus
from nexus_constructor.geometry.no_shape_geometry import OFFCube
from PySide2.QtGui import QVector3D


def test_GIVEN_nothing_WHEN_constructing_NoShapeGeometry_THEN_off_geometry_returns_an_OFFCube():
    geom = NoShapeGeometry()
    assert geom.off_geometry == OFFCube


def test_GIVEN_nothing_WHEN_constructing_NoShapeGeometry_THEN_geometry_str_is_None():
    geom = NoShapeGeometry()
    assert geom.geometry_str == "None"


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


def test_GIVEN_nothing_WHEN_calling_off_geometry_on_noshapegeometry_THEN_OFFCube_is_returned():
    geom = NoShapeGeometry()
    assert geom.off_geometry == OFFCube


def test_GIVEN_off_gemetry_WHEN_calling_off_geometry_on_offGeometry_THEN_original_geometry_is_returned():
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
