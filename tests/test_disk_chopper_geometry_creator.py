import pytest
import numpy as np

from nexus_constructor.geometry.disk_chopper.disk_chopper_geometry_creator import (
    Point,
    DiskChopperGeometryCreator,
    THICKNESS,
    ARROW_SIZE,
    RESOLUTION,
)

POINT_X = 2.0
POINT_Y = 3.0
POINT_Z = 4.0

R = np.sqrt(2)
THETA = np.deg2rad(45)


@pytest.fixture(scope="function")
def point():
    return Point(POINT_X, POINT_Y, POINT_Z)


@pytest.fixture(scope="function")
def geometry_creator(chopper_details):
    return DiskChopperGeometryCreator(chopper_details)


def test_GIVEN_three_values_WHEN_creating_point_THEN_point_is_initialised_correctly(
    point
):

    assert point.x == POINT_X
    assert point.y == POINT_Y
    assert point.z == POINT_Z


def test_GIVEN_id_WHEN_point_has_no_id_THEN_id_is_set(point):

    id = 300
    point.set_id(id)
    assert point.id == id


def test_GIVEN_id_WHEN_point_already_has_id_THEN_id_doesnt_change(point):

    old_id = 200
    new_id = 300
    point.set_id(old_id)
    point.set_id(new_id)

    assert point.id == old_id


def test_GIVEN_non_integer_id_WHEN_setting_id_THEN_id_is_rejected(point):

    bad_id = "abc"
    point.set_id(bad_id)
    assert point.id is None


def test_GIVEN_point_WHEN_calling_point_to_qvector3d_THEN_expected_vector_is_created(
    point
):

    vector = point.point_to_qvector3d()
    assert vector.x() == POINT_X
    assert vector.y() == POINT_Y
    assert vector.z() == POINT_Z


def test_GIVEN_chopper_details_WHEN_initialising_geometry_creator_THEN_geometry_creator_is_initialised_with_expected_values(
    geometry_creator, chopper_details
):

    expected_z = THICKNESS * 2

    assert geometry_creator.faces == []
    assert geometry_creator.z == expected_z
    assert geometry_creator.arrow_size == ARROW_SIZE
    assert geometry_creator.resolution == RESOLUTION

    assert geometry_creator._radius == chopper_details.radius
    assert np.array_equal(geometry_creator._slit_edges, chopper_details.slit_edges)
    assert geometry_creator._slit_height == chopper_details.slit_height
    assert geometry_creator._slits == chopper_details.slits

    assert len(geometry_creator.points) == 2

    expected_points = [Point(0, 0, expected_z), Point(0, 0, -expected_z)]

    for i in range(2):
        assert geometry_creator.points[i] == expected_points[i]


def test_GIVEN_polar_coordinates_WHEN_converting_polar_to_cartesian_THEN_expected_values_are_returned(
    geometry_creator
):
    x, y = geometry_creator._polar_to_cartesian_2d(R, THETA)
    assert abs(x - 1) < 1e-05
    assert abs(y - 1) < 1e-05


def test_GIVEN_polar_coordinates_WHEN_creating_mirrored_points_THEN_expected_points_are_returned(
    geometry_creator
):

    expected_first_point = Point(1.0, 1.0, THICKNESS * 2)
    expected_second_point = Point(1.0, 1.0, -THICKNESS * 2)

    actual_first_point, actual_second_point = geometry_creator._create_mirrored_points(
        R, THETA
    )
    assert actual_first_point == expected_first_point
    assert actual_second_point == expected_second_point
