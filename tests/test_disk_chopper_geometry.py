import pytest

from nexus_constructor.geometry.disk_chopper_geometry import ChopperDetails


@pytest.fixture
def chopper_details(scope="function"):
    return ChopperDetails(
        slits=3, slit_edges=[0, 43, 82, 150, 220, 250], radius=200, slit_height=70
    )


def test_GIVEN_valid_values_WHEN_validating_chopper_details_THEN_returns_true(
    chopper_details
):

    assert chopper_details.validate()


def test_GIVEN_slit_edges_list_contains_non_float_or_int_values_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details.slit_edges[3] = None
    assert not chopper_details.validate()


def test_GIVEN_mismatch_between_slits_and_slit_edges_array_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details._slits = 5
    assert not chopper_details.validate()


def test_GIVEN_slit_height_is_larger_than_radius_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details._slit_height = 201
    assert not chopper_details.validate()


def test_GIVEN_slit_height_and_radius_are_equal_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details._slit_height = chopper_details._radius = 20
    assert not chopper_details.validate()


def test_GIVEN_slit_edges_list_is_not_in_order_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details.slit_edges[0], chopper_details.slit_edges[1] = (
        chopper_details.slit_edges[1],
        chopper_details.slit_edges[0],
    )
    assert not chopper_details.validate()


def test_GIVEN_slit_edges_list_contains_repeated_values_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details.slit_edges[0] = chopper_details.slit_edges[1]
    assert not chopper_details.validate()


def test_GIVEN_slit_edges_list_has_overlapping_slits_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details.slit_edges[-1] = 365
    assert not chopper_details.validate()
