import pytest
import numpy as np
from nexus_constructor.geometry.disk_chopper.chopper_details import ChopperDetails

N_SLITS = 3
RADIUS_LENGTH = 200.3
SLIT_HEIGHT_LENGTH = 70.1
EXPECTED_Z = RADIUS_LENGTH * 0.025


def degree_to_radian(x):
    return np.deg2rad(x) % (np.pi * 2)


CONVERT_DEGREES_TO_RADIANS = np.vectorize(degree_to_radian)


DEGREES_EDGES_ARR = [0.0, 43.4, 82.6, 150.1, 220.0, 250.3]
RADIANS_EDGES_ARR = CONVERT_DEGREES_TO_RADIANS(DEGREES_EDGES_ARR)


@pytest.fixture(scope="function")
def chopper_details():
    return ChopperDetails(
        slits=N_SLITS,
        slit_edges=np.copy(RADIANS_EDGES_ARR),
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        angle_units="rad",
        slit_height_units="m",
        radius_units="m",
    )
