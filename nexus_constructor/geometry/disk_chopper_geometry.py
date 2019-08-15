from math import pi
from typing import List

from numpy.core.umath import deg2rad


class ChopperDetails:

    TWO_PI = pi * 2

    def __init__(
        self,
        slits: int,
        slit_edges: List,
        radius: float,
        slit_height: float,
        units: str = "deg",
    ):
        """
        Class for storing and validating chopper input given by a user.
        :param slits: The number of slits in the disk chopper.
        :param slit_edges: The list of slit edge angles in the disk chopper.
        :param radius: The radius of the slit chopper.
        :param slit_height: The slit height.
        :param units: The units of the slit edges. At the moment all slit edges provided are assumed to be degrees
            because the faculty for specifying attributes of fields hasn't yet been implemented in the
            Add Component Dialog.
        """
        self._slits = slits
        self._slit_edges = slit_edges
        self._radius = radius
        self._slit_height = slit_height
        self._units = units

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

    def validate(self):

        # Check that all the elements in the slit edge list are either int or float
        for edge in self._slit_edges:
            if type(edge) is not float and type(edge) is not int:
                return False

        # Check that the number of slit edges is equal to two times the number of slits
        if len(self._slit_edges) != 2 * self._slits:
            return False

        # Check that the slit height is smaller than the radius
        if self._slit_height >= self._radius:
            return False

        # Check that the list of slit edges is sorted
        if self._slit_edges != sorted(self._slit_edges):
            return False

        # Check that there are no repeated angles
        if len(self._slit_edges) != len(set(self._slit_edges)):
            return False

        # Convert the angles to radians (if necessary) and make sure they are all less then two pi
        if self._units == "deg":
            self._slit_edges = [
                deg2rad(edge) % ChopperDetails.TWO_PI for edge in self._slit_edges
            ]
        else:
            self._slit_edges = [
                edge % ChopperDetails.TWO_PI for edge in self._slit_edges
            ]

        # Check that the first and last edges do not overlap
        if (self._slit_edges != sorted(self._slit_edges)) and (
            self._slit_edges[-1] >= self._slit_edges[0]
        ):
            return False

        return True
