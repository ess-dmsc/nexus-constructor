import pytest
import numpy as np

from nexus_constructor.geometry.disk_chopper.disk_chopper_geometry_creator import (
    Point,
    DiskChopperGeometryCreator,
    HALF_THICKNESS,
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


def expected_slit_boundary_face_points(center_to_slit_start: float, radius: float):
    """
    Creates for points that match the expected points for the face for the slit boundary. Assumes the slit edge has an
    angle of zero.
    :param center_to_slit_start: Distance from disk chopper center to the beginning of the slit.
    :param radius: The radius of the disk chopper.
    :return: Four points that should be roughly equal to the points for slit boundary face.
    """
    expected_upper_front = Point(radius, 0, HALF_THICKNESS)
    expected_lower_front = Point(center_to_slit_start, 0, HALF_THICKNESS)
    expected_upper_back = Point(radius, 0, -HALF_THICKNESS)
    expected_lower_back = Point(center_to_slit_start, 0, -HALF_THICKNESS)

    return (
        expected_lower_back,
        expected_lower_front,
        expected_upper_back,
        expected_upper_front,
    )


def create_two_points():
    """
    Create two points for testing the face connected to front/back centre methods.
    """
    first_point = Point(3, 4, 5)
    first_point.set_id(10)
    second_point = Point(6, 7, 8)
    second_point.set_id(11)

    return first_point, second_point


def test_GIVEN_three_values_WHEN_creating_point_THEN_point_is_initialised_correctly(
    point
):

    assert point.x == POINT_X
    assert point.y == POINT_Y
    assert point.z == POINT_Z
    assert point.id is None


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

    expected_z = HALF_THICKNESS

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

    expected_first_point = Point(1.0, 1.0, HALF_THICKNESS)
    expected_second_point = Point(1.0, 1.0, -HALF_THICKNESS)

    actual_first_point, actual_second_point = geometry_creator._create_mirrored_points(
        R, THETA
    )
    assert actual_first_point == expected_first_point
    assert actual_second_point == expected_second_point


def test_GIVEN_face_should_look_right_WHEN_creating_and_adding_point_set_THEN_expected_face_is_created_with_expected_order(
    geometry_creator
):
    radius = 1
    center_to_slit_start = 0.5
    slit_edge = 0
    right_facing = False

    # Create the expected points
    expected_lower_back, expected_lower_front, expected_upper_back, expected_upper_front = expected_slit_boundary_face_points(
        center_to_slit_start, radius
    )

    # Call the create and add point set method
    actual_upper_front, actual_upper_back, actual_lower_front, actual_lower_back = geometry_creator.create_and_add_point_set(
        radius, center_to_slit_start, slit_edge, right_facing
    )

    # Check that the return points match the expected points
    assert expected_upper_front == actual_upper_front
    assert expected_lower_front == actual_lower_front
    assert expected_upper_back == actual_upper_back
    assert expected_lower_back == actual_lower_back

    # Check that the points have been added to the list
    assert actual_upper_front in geometry_creator.points
    assert actual_lower_front in geometry_creator.points
    assert actual_upper_back in geometry_creator.points
    assert actual_lower_back in geometry_creator.points

    # Check that the face created from the four points has the expected winding order
    expected_winding_order = [
        actual_lower_front.id,
        actual_upper_front.id,
        actual_upper_back.id,
        actual_lower_back.id,
    ]
    assert expected_winding_order == geometry_creator.faces[-1]


def test_GIVEN_face_should_look_left_WHEN_creating_and_adding_point_set_THEN_expected_face_is_created_with_expected_point_order(
    geometry_creator
):
    radius = 1
    center_to_slit_start = 0.5
    slit_edge = 0
    right_facing = True

    # Create the expected points
    expected_lower_back, expected_lower_front, expected_upper_back, expected_upper_front = expected_slit_boundary_face_points(
        center_to_slit_start, radius
    )

    # Call the create and add point set method
    actual_upper_front, actual_upper_back, actual_lower_front, actual_lower_back = geometry_creator.create_and_add_point_set(
        radius, center_to_slit_start, slit_edge, right_facing
    )

    # Check that the return points match the expected points
    assert expected_upper_front == actual_upper_front
    assert expected_lower_front == actual_lower_front
    assert expected_upper_back == actual_upper_back
    assert expected_lower_back == actual_lower_back

    # Check that the points have been added to the list
    assert actual_upper_front in geometry_creator.points
    assert actual_lower_front in geometry_creator.points
    assert actual_upper_back in geometry_creator.points
    assert actual_lower_back in geometry_creator.points

    # Check that the face created from the four points has the expected winding order
    expected_winding_order = [
        actual_lower_back.id,
        actual_upper_back.id,
        actual_upper_front.id,
        actual_lower_front.id,
    ]
    assert expected_winding_order == geometry_creator.faces[-1]


def test_GIVEN_r_and_theta_WHEN_creating_and_adding_mirrored_points_THEN_expected_points_are_created_and_added_to_list(
    geometry_creator
):

    r = 20
    theta = 0

    expected_front_point = Point(r, 0, HALF_THICKNESS)
    expected_back_point = Point(r, 0, -HALF_THICKNESS)

    actual_front_point, actual_back_point = geometry_creator.create_and_add_mirrored_points(
        r, theta
    )

    assert expected_front_point == actual_front_point
    assert expected_back_point == actual_back_point

    assert actual_front_point in geometry_creator.points
    assert actual_back_point in geometry_creator.points


def test_GIVEN_points_WHEN_adding_face_connected_to_front_centre_THEN_expected_face_is_created(
    geometry_creator
):

    first_point, second_point = create_two_points()

    geometry_creator.add_face_connected_to_front_centre([first_point, second_point])
    expected_face = [geometry_creator.front_centre.id, first_point.id, second_point.id]
    assert expected_face == geometry_creator.faces[-1]


def test_GIVEN_points_WHEN_adding_face_connected_to_back_centre_THEN_expected_face_is_created(
    geometry_creator
):

    first_point, second_point = create_two_points()
    geometry_creator.add_face_connected_to_back_centre([first_point, second_point])

    expected_face = [geometry_creator.back_centre.id, first_point.id, second_point.id]
    assert expected_face == geometry_creator.faces[-1]


def test_GIVEN_point_WHEN_adding_point_to_list_THEN_point_is_added_and_assigned_an_id(
    geometry_creator
):

    point = Point(1, 2, 3)
    geometry_creator._add_point_to_list(point)

    assert point in geometry_creator.points
    assert point.id == len(geometry_creator.points) - 1


def test_GIVEN_set_of_points_WHEN_adding_face_to_list_THEN_list_of_ids_is_added_to_list_of_faces(
    geometry_creator
):

    num_points = 3
    points = []
    ids = []

    for i in range(num_points):
        ids.append(i + 2)
        points.append(Point(i, i, i))
        points[-1].set_id(ids[-1])

    geometry_creator.add_face_to_list(points)

    assert ids in geometry_creator.faces
