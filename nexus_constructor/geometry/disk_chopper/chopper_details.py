import numpy as np

from nexus_constructor.unit_utils import calculate_unit_conversion_factor

TWO_PI = np.pi * 2


class ChopperDetails:
    def __init__(
        self,
        slits: int,
        slit_edges: np.ndarray,
        radius: float,
        slit_height: float,
        angle_units: str,
        slit_height_units: str,
        radius_units: str,
    ):
        """
        Class for storing the chopper input given by the user.
        :param slits: The number of slits in the disk chopper.
        :param slit_edges: The list of slit edge angles in the disk chopper.
        :param radius: The radius of the slit chopper.
        :param slit_height: The slit height.
        :param angle_units: The units of the slit edges. At the moment all slit edges provided are assumed to be degrees
            because the faculty for specifying attributes of fields hasn't yet been implemented in the Add Component
            Dialog.
        :param slit_height_units: The units for the slit length.
        :param radius_units: The units for the radius.
        """
        self._slits = slits
        self._radius = radius
        self._slit_height = slit_height

        # Convert the angles to radians and make sure they are all less then two pi
        slit_edges_factor = calculate_unit_conversion_factor(angle_units, "radians")
        self._slit_edges = [edge * slit_edges_factor % TWO_PI for edge in slit_edges]

        self._slit_height *= calculate_unit_conversion_factor(
            slit_height_units, "metres"
        )
        self._radius *= calculate_unit_conversion_factor(radius_units, "metres")

    @property
    def slits(self):
        return self._slits

    @property
    def slit_edges(self):
        return self._slit_edges

    @property
    def radius(self):
        return self._radius

    @property
    def slit_height(self):
        return self._slit_height
