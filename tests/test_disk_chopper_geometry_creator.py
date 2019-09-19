import pytest

from nexus_constructor.geometry.disk_chopper.disk_chopper_geometry_creator import Point

POINT_X = 2.0
POINT_Y = 3.0
POINT_Z = 4.0


@pytest.fixture(scope="function")
def point():
    return Point(POINT_X, POINT_Y, POINT_Z)


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
