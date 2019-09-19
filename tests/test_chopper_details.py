import numpy as np
import pytest

from nexus_constructor.geometry.disk_chopper.chopper_details import ChopperDetails
from tests.test_disk_chopper_checker import (
    N_SLITS,
    EDGES_ARR,
    RADIUS_LENGTH,
    SLIT_HEIGHT_LENGTH,
    CONVERT_DEGREES_TO_RADIANS,
)


@pytest.fixture(scope="function")
def chopper_details():
    return ChopperDetails(
        slits=N_SLITS,
        slit_edges=EDGES_ARR,
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        angle_units="rad",
        slit_height_units="m",
        radius_units="m",
    )


def test_GIVEN_chopper_information_WHEN_initialising_chopper_details_THEN_chopper_details_object_contains_original_disk_chopper_info(
    chopper_details
):

    assert chopper_details.slits == N_SLITS
    assert np.array_equal(chopper_details.slit_edges, EDGES_ARR)
    assert chopper_details.radius == RADIUS_LENGTH
    assert chopper_details.slit_height == SLIT_HEIGHT_LENGTH


def test_GIVEN_angles_in_degrees_WHEN_initialising_chopper_details_object_THEN_angles_are_converted_to_radians():

    edges_array = np.array([i * 30 for i in range(4)])

    chopper_details = ChopperDetails(
        slits=N_SLITS,
        slit_edges=np.array([i * 30 for i in range(4)]),
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        angle_units="deg",
        slit_height_units="m",
        radius_units="m",
    )

    assert np.array_equal(
        chopper_details.slit_edges, CONVERT_DEGREES_TO_RADIANS(edges_array)
    )


def test_GIVEN_slit_height_length_in_cm_WHEN_initialising_chopper_details_THEN_slit_height_is_converted_to_cm():

    chopper_details = ChopperDetails(
        slits=N_SLITS,
        slit_edges=EDGES_ARR,
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        angle_units="deg",
        slit_height_units="cm",
        radius_units="m",
    )

    assert chopper_details.slit_height * 100 == SLIT_HEIGHT_LENGTH


def test_GIVEN_radius_length_in_cm_WHEN_initialising_chopper_details_THEN_radius_is_converted_to_cm():

    chopper_details = ChopperDetails(
        slits=N_SLITS,
        slit_edges=EDGES_ARR,
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        angle_units="deg",
        radius_units="cm",
        slit_height_units="m",
    )

    assert chopper_details.radius * 100 == RADIUS_LENGTH
