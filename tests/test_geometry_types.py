from nexus_constructor.geometry_types import (
    Geometry,
    NoShapeGeometry,
    CylindricalGeometry,
    OFFGeometry,
    OFFCube,
    QVector3D,
    QMatrix4x4,
    acos,
    degrees,
)
from pytest import raises

# Test:
#


def test_GIVEN_nothing_WHEN_constructing_Geometry_THEN_AbstractError():
    with raises(TypeError):
        Geometry()


def test_GIVEN_nothing_WHEN_constructing_NoShapeGeometry_THEN_off_geometry_returns_offcube():
    geom = NoShapeGeometry()
    assert geom.off_geometry == OFFCube


def test_GIVEN_nothing_WHEN_constructing_NoShapeGeometry_THEN_geometry_str_is_none():
    geom = NoShapeGeometry()
    assert geom.geometry_str == "None"


def test_GIVEN_nothing_WHEN_constructing_CylindricalGeometry_THEN_geometry_str_is_correct():
    geom = CylindricalGeometry()
    assert geom.geometry_str == "Cylinder"


def test_GIVEN_nothing_WHEN_constructing_OFFGeometry_THEN_geometry_str_is_correct():
    geom = OFFGeometry()
    assert geom.geometry_str == "OFF"


def test_GIVEN_cylinder_WHEN_constructing_CylindricalGeometry_THEN_off_geometry_returns_correct_off():
    unit = "m"
    axis_direction = QVector3D(1, 2, 3)
    height = 2.0
    radius = 1.0

    geom = CylindricalGeometry(unit, axis_direction, height, radius)

    assert geom.radius == radius
    assert geom.height == height
    assert geom.axis_direction.toTuple() == axis_direction.toTuple()
    assert geom.units == unit


def test_GIVEN_nothing_WHEN_constructing_CylindricalGeometry_THEN_rotation_matrix_is_correct():
    unit = "m"
    axis_direction = QVector3D(1, 2, 3)
    height = 2.0
    radius = 1.0

    geom = CylindricalGeometry(unit, axis_direction, height, radius)

    default_axis = QVector3D(0, 0, 1)
    cross_product = QVector3D.crossProduct(axis_direction.normalized(), default_axis)
    rotate_radians = acos(
        QVector3D.dotProduct(axis_direction.normalized(), default_axis)
    )
    matrix = QMatrix4x4()
    matrix.rotate(degrees(rotate_radians), cross_product)
    assert geom.rotation_matrix == matrix


def test_GIVEN_faces_WHEN_calling_winding_order_on_OFF_THEN_order_is_correct():
    vertices = [
        QVector3D(0,0,1),
        QVector3D(0,1,0),
        QVector3D(0,0,0),
        QVector3D(0,1,1),
    ]

    faces = [[0,1,2,3]]

    geom = OFFGeometry(vertices, faces)
    expected = [point for face in faces for point in face]

    assert expected == geom.winding_order
