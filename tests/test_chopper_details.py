import numpy as np
import pytest
from nexus_constructor.geometry.disk_chopper.chopper_details import ChopperDetails
from tests.chopper_test_helpers import (
    N_SLITS,
    RADIUS_LENGTH,
    SLIT_HEIGHT_LENGTH,
    CONVERT_DEGREES_TO_RADIANS,
    RADIANS_EDGES_ARR,
    DEGREES_EDGES_ARR,
)


def test_GIVEN_initialised_chopper_details_WHEN_getting_properties_THEN_values_returned_match_original_constructor_input(
    chopper_details
):
    # ChopperDetails is constructed in the test fixture
    assert chopper_details.slits == N_SLITS
    assert np.allclose(chopper_details.slit_edges, RADIANS_EDGES_ARR)
    assert chopper_details.radius == RADIUS_LENGTH
    assert chopper_details.slit_height == pytest.approx(SLIT_HEIGHT_LENGTH)


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

    assert np.allclose(
        chopper_details.slit_edges, CONVERT_DEGREES_TO_RADIANS(edges_array)
    )


def test_GIVEN_slit_height_length_in_cm_WHEN_initialising_chopper_details_THEN_slit_height_is_converted_to_m():
    chopper_details = ChopperDetails(
        slits=N_SLITS,
        slit_edges=DEGREES_EDGES_ARR,
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        angle_units="deg",
        slit_height_units="cm",
        radius_units="m",
    )

    assert chopper_details.slit_height * 100 == pytest.approx(SLIT_HEIGHT_LENGTH)


def test_GIVEN_radius_length_in_cm_WHEN_initialising_chopper_details_THEN_radius_is_converted_to_m():
    chopper_details = ChopperDetails(
        slits=N_SLITS,
        slit_edges=DEGREES_EDGES_ARR,
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        angle_units="deg",
        radius_units="cm",
        slit_height_units="m",
    )

    assert chopper_details.radius * 100 == pytest.approx(RADIUS_LENGTH)
