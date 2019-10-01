import pytest
import numpy as np
from nexus_constructor.geometry.disk_chopper.chopper_details import ChopperDetails

N_SLITS = 3
EDGES_ARR = np.array(
    [
        0.0,
        0.757472895365539,
        1.4416419621473162,
        2.6197392072434886,
        3.839724354387525,
        4.368559117741807,
    ]
)
RADIUS_LENGTH = 200.3
SLIT_HEIGHT_LENGTH = 70.1
EXPECTED_Z = RADIUS_LENGTH * 0.025


def degree_to_radian(x):
    return np.deg2rad(x) % (np.pi * 2)


CONVERT_DEGREES_TO_RADIANS = np.vectorize(degree_to_radian)


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
