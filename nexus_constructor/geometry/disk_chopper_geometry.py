from math import pi

from PySide2.QtWidgets import QListWidget
from numpy import diff, unique
from numpy.core.umath import deg2rad, ndarray

from nexus_constructor.validators import DATASET_TYPE

SLIT_EDGES = "slit_edges"
SLITS = "slits"
RADIUS = "radius"
SLIT_HEIGHT = "slit_height"

REQUIRED_CHOPPER_FIELDS = [SLIT_EDGES, SLITS, RADIUS, SLIT_HEIGHT]
CONTAINS_INTEGER = [
    DATASET_TYPE[key] for key in DATASET_TYPE.keys() if "Integer" in key
]
CONTAINS_SHORT = [DATASET_TYPE[key] for key in DATASET_TYPE.keys() if "Short" in key]
CONTAINS_LONG = [DATASET_TYPE[key] for key in DATASET_TYPE.keys() if "Long" in key]
INT_TYPES = CONTAINS_INTEGER + CONTAINS_SHORT + CONTAINS_LONG

FLOAT_TYPES = [
    DATASET_TYPE[key] for key in DATASET_TYPE.keys() if key in ["Float", "Double"]
]


class ChopperChecker:
    def __init__(self, fields_widget: QListWidget):

        self.fields_widget = fields_widget
        self.fields_dict = {
            widget.name: widget for widget in self.fields_widget.items()
        }

        self._slits = None
        self._slit_edges = None
        self._radius = None
        self._slit_height = None
        self._units = "deg"

    def validate_chopper(self):

        return (
            self.required_fields_present()
            and self.fields_have_correct_type()
            and self.edges_array_has_correct_shape()
            and self.input_describes_valid_chopper()
        )

    def required_fields_present(self):
        """
        Carries out a preliminary check of the fields input to see if seems like it might be describing a
        valid disk chopper shape.
        :param fields_widget:
        :return:
        """
        return set(self.fields_dict.keys()) == set(REQUIRED_CHOPPER_FIELDS)

    def fields_have_correct_type(self):

        return (
            self.fields_dict[SLITS].dtype in INT_TYPES
            and self.fields_dict[RADIUS].dtype in FLOAT_TYPES
            and self.fields_dict[SLIT_HEIGHT].dtype in FLOAT_TYPES
            and self.fields_dict[SLIT_EDGES].dtype in FLOAT_TYPES
        )

    def edges_array_has_correct_shape(self):

        edges_dim = self.fields_dict[SLIT_EDGES].value.ndim

        if edges_dim > 2:
            return False

        if edges_dim == 2:
            edges_shape = self.fields_dict[SLIT_EDGES].value.shape
            if not edges_shape[0] == 1 or edges_shape[1] == 1:
                return False

        return True

    def input_describes_valid_chopper(self):

        self._slit_edges = self.fields_dict[SLIT_EDGES].value
        self._radius = self.fields_dict[RADIUS].value
        self._slit_height = self.fields_dict[SLIT_HEIGHT].value
        self._slits = self.fields_dict[SLITS].value

        # Check that the number of slit edges is equal to two times the number of slits
        if len(self._slit_edges) != 2 * self._slits:
            return False

        # Check that the slit height is smaller than the radius
        if self._slit_height >= self._radius:
            return False

        # Check that the list of slit edges is sorted
        if not (diff(self._slit_edges) >= 0).all():
            return False

        # Check that there are no repeated angles
        if len(self._slit_edges) != len(unique(self._slit_edges)):
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

    def get_chopper_details(self):
        return ChopperDetails(
            self._slits, self._slit_edges, self._radius, self._slit_height
        )


class ChopperDetails:

    TWO_PI = pi * 2

    def __init__(
        self,
        slits: int,
        slit_edges: ndarray,
        radius: float,
        slit_height: float,
        units: str = "deg",
    ):
        """
        Class for storing the chopper input given by the user.
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
