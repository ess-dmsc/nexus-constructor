from nexus_constructor.data_model import CylindricalGeometry, Vector
from pytest import approx, raises


def test_x_axis_aligned_cylindrical_geometry_points():
    height = 3
    radius = 4
    cylinder = CylindricalGeometry(axis_direction=Vector(1, 0, 0),
                                   height=height,
                                   radius=radius)

    assert cylinder.base_center_point == Vector(0, 0, 0)

    assert cylinder.base_edge_point.x == approx(0)
    assert cylinder.base_edge_point.y ** 2 + cylinder.base_edge_point.z ** 2 == approx(radius ** 2)

    assert cylinder.top_center_point.x == approx(height)
    assert cylinder.top_center_point.y == approx(0)
    assert cylinder.top_center_point.z == approx(0)


def test_y_axis_aligned_cylindrical_geometry_points():
    height = 3
    radius = 5
    cylinder = CylindricalGeometry(axis_direction=Vector(0, 1, 0),
                                   height=height,
                                   radius=radius)

    assert cylinder.base_center_point == Vector(0, 0, 0)

    assert cylinder.base_edge_point.y == approx(0)
    assert cylinder.base_edge_point.x ** 2 + cylinder.base_edge_point.z ** 2 == approx(radius ** 2)

    assert cylinder.top_center_point.x == approx(0)
    assert cylinder.top_center_point.y == approx(height)
    assert cylinder.top_center_point.z == approx(0)


def test_z_axis_aligned_cylindrical_geometry_points():
    height = 3
    radius = 5
    cylinder = CylindricalGeometry(axis_direction=Vector(0, 0, 1),
                                   height=height,
                                   radius=radius)

    assert cylinder.base_center_point == Vector(0, 0, 0)

    assert cylinder.base_edge_point.z == approx(0)
    assert cylinder.base_edge_point.x ** 2 + cylinder.base_edge_point.y ** 2 == approx(radius ** 2)

    assert cylinder.top_center_point.x == approx(0)
    assert cylinder.top_center_point.y == approx(0)
    assert cylinder.top_center_point.z == approx(height)


def test_axis_direction_must_be_non_zero():
    with raises(ValueError):
        CylindricalGeometry(axis_direction=Vector(0, 0, 0))
