from typing import Sequence

from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QListWidget
import numpy as np
from h5py import Group

from nexus_constructor.geometry import OFFGeometryNoNexus
from nexus_constructor.nexus.nexus_wrapper import decode_bytes_string
from nexus_constructor.unit_converter import calculate_unit_conversion_factor
from nexus_constructor.validators import DATASET_TYPE

SLIT_EDGES = "slit_edges"
SLITS = "slits"
RADIUS = "radius"
SLIT_HEIGHT = "slit_height"
NAME = "name"

UNABLE = "Unable to create chopper geometry - "
EXPECTED_TYPE_ERROR_MSG = {
    SLIT_EDGES: "float",
    SLITS: "int",
    RADIUS: "float",
    SLIT_HEIGHT: "float",
}

REQUIRED_CHOPPER_FIELDS = {SLIT_EDGES, SLITS, RADIUS, SLIT_HEIGHT}
INT_TYPES = [value for value in DATASET_TYPE.values() if "int" in str(value)]
FLOAT_TYPES = [value for value in DATASET_TYPE.values() if "float" in str(value)]

TWO_PI = np.pi * 2


def check_data_type(data_type, expected_types):
    try:
        return data_type.dtype in expected_types
    except AttributeError:
        return False


def incorrect_field_type_message(fields_dict: dict, field_name: str):
    """
    Creates a string explaining to the user that the field input did not have the expected type.
    :param field_name: The name of the field that failed the check.
    :return: A string that contains the name of the field, the type it should have, and the type the user entered.
    """
    return "Wrong {} type. Expected {} but found {}.".format(
        field_name, EXPECTED_TYPE_ERROR_MSG[field_name], type(fields_dict[field_name])
    )


def fields_have_correct_type(fields_dict: dict):

    correct_slits_type = check_data_type(fields_dict[SLITS], INT_TYPES)
    correct_radius_type = check_data_type(fields_dict[RADIUS], FLOAT_TYPES)
    correct_slit_height_type = check_data_type(fields_dict[SLIT_HEIGHT], FLOAT_TYPES)
    correct_slit_edges_type = check_data_type(fields_dict[SLIT_EDGES], FLOAT_TYPES)

    if (
        correct_slits_type
        and correct_radius_type
        and correct_slit_height_type
        and correct_slit_edges_type
    ):
        return True

    problems = []

    if not correct_slits_type:
        problems.append(incorrect_field_type_message(fields_dict, SLITS))

    if not correct_radius_type:
        problems.append(incorrect_field_type_message(fields_dict, RADIUS))

    if not correct_slit_height_type:
        problems.append(incorrect_field_type_message(fields_dict, SLIT_HEIGHT))

    if not correct_slit_edges_type:
        problems.append(incorrect_field_type_message(fields_dict, SLIT_EDGES))

    print(UNABLE + "\n".join(problems))
    return False


def edges_array_has_correct_shape(edges_dim: int, edges_shape: tuple):
    """
    Checks that the edges array consists of either one row or one column.
    :return: True if the edges array is 1D. False otherwise.
    """
    if edges_dim > 2:
        print(
            UNABLE
            + "Expected slit edges array to be 1D but it has {} dimensions.".format(
                edges_dim
            )
        )
        return False

    if edges_dim == 2:
        if edges_shape[0] != 1 and edges_shape[1] != 1:
            print(
                UNABLE
                + "Expected slit edges array to be 1D but it has shape {}.".format(
                    edges_shape
                )
            )
            return False

    return True


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

        # Convert the angles to radians (if necessary) and make sure they are all less then two pi
        if angle_units == "deg":
            self._slit_edges = [np.deg2rad(edge) % TWO_PI for edge in slit_edges]
        else:
            self._slit_edges = [edge % TWO_PI for edge in slit_edges]

        # Something should check that the units a valid before we get to this point
        if slit_height_units != "m":

            factor = calculate_unit_conversion_factor(slit_height_units)
            self._slit_height *= factor

        if radius_units != "m":

            factor = calculate_unit_conversion_factor(radius_units)
            self._radius *= factor

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


def input_describes_valid_chopper(
    chopper_details: ChopperDetails, slit_edges: Sequence
):
    """
    A final check that the input has the following properties:
        - The length of the slit edges array is twice the number of slits
        - The slit height is smaller than the radius
        - The slit edges array is sorted.
        - The slit edges array doesn't contain repeated angles.
        - The slit edges array doesn't contain overlapping slits.
    If this is all true then a chopper mesh can be created.
    :return: True if all the conditions above are met. False otherwise.
    """
    # Check that the number of slit edges is equal to two times the number of slits
    if len(chopper_details.slit_edges) != 2 * chopper_details.slits:
        print(
            UNABLE
            + "Size of slit edges array should be twice the number of slits. Instead there are {} slits and {} slit edges.".format(
                chopper_details.slits, len(chopper_details.slit_edges)
            )
        )
        return False

    # Check that the slit height is smaller than the radius
    if chopper_details.slit_height >= chopper_details.radius:
        print(
            UNABLE
            + "Slit height should be smaller than radius. Instead slit height is {} and radius is {}".format(
                chopper_details.slit_height, chopper_details.radius
            )
        )
        return False

    # Check that the list of slit edges is sorted
    if not (np.diff(slit_edges) >= 0).all():
        print(UNABLE + "Slit edges array is not sorted. Found values:", slit_edges)
        return False

    # Check that there are no repeated angles
    if len(slit_edges) != len(np.unique(slit_edges)):
        print(
            UNABLE + "Angles in slit edges array should be unique. Found values:",
            slit_edges,
        )
        return False

    # Check that the first and last edges do not overlap
    if (chopper_details.slit_edges != sorted(chopper_details.slit_edges)) and (
        chopper_details.slit_edges[-1] >= chopper_details.slit_edges[0]
    ):
        print(
            UNABLE + "Slit edges contains overlapping slits. Found values:", slit_edges
        )
        return False

    return True


class UserDefinedChopperChecker:
    def __init__(self, fields_widget: QListWidget):

        self.fields_dict = dict()

        self._angle_units = "deg"
        self._slit_height_units = "m"
        self._radius_units = "m"
        self._chopper_details = None

        for i in range(fields_widget.count()):
            widget = fields_widget.itemWidget(fields_widget.item(i))
            self.fields_dict[widget.name] = widget

    def required_fields_present(self):
        """
        Checks that all of the fields required to create the disk chopper are present.
        :return: True if all the required fields are present. False otherwise.
        """
        missing_fields = REQUIRED_CHOPPER_FIELDS - self.fields_dict.keys()

        if len(missing_fields) > 0:
            print(UNABLE + "Required field(s) missing:", ", ".join(missing_fields))
            return False

        return True

    def get_chopper_details(self):
        """
        :return: The ChopperDetails object. This will only be created if `validate_chopper` was called and the
            validation was successful. Otherwise this method just returns None.
        """
        return self._chopper_details

    def validate_chopper(self):
        """
        Performs the following checks in order to determine if the chopper input is valid: 1) Checks that the required
        fields are present, 2) Checks that the fields have the correct type, 3) Checks that the slit edges array is 1D,
        and 4) Checks that the overall chopper geometry is valid (no overlapping slits, repeated angles, etc).
        :return: True if the chopper is valid. False otherwise.
        """
        if not (
            self.required_fields_present()
            and fields_have_correct_type(self.fields_dict)
            and edges_array_has_correct_shape(
                self.fields_dict[SLIT_EDGES].value.ndim,
                self.fields_dict[SLIT_EDGES].value.shape,
            )
        ):
            return False

        self._chopper_details = ChopperDetails(
            self.fields_dict[SLITS].value,
            self.fields_dict[SLIT_EDGES].value,
            self.fields_dict[RADIUS].value,
            self.fields_dict[SLIT_HEIGHT].value,
            self._angle_units,
            self._slit_height_units,
            self._radius_units,
        )

        return input_describes_valid_chopper(
            self._chopper_details, self.fields_dict[SLIT_EDGES].value
        )


class NexusDefinedChopperChecker:
    def __init__(self, disk_chopper: Group):

        self.fields_dict = dict()

        self._angle_units = None
        self._slit_height_units = None
        self._radius_units = None
        self._chopper_details = None

        self._disk_chopper = disk_chopper

    def get_chopper_details(self):
        """
        :return: The ChopperDetails object. This will only be created if `validate_chopper` was called and the
            validation was successful. Otherwise this method just returns None.
        """
        return self._chopper_details

    def required_fields_present(self):

        try:

            self.fields_dict[SLITS] = self._disk_chopper[SLITS][()]
            self.fields_dict[SLIT_EDGES] = self._disk_chopper[SLIT_EDGES][()]
            self.fields_dict[RADIUS] = self._disk_chopper[RADIUS][()]
            self.fields_dict[SLIT_HEIGHT] = self._disk_chopper[SLIT_HEIGHT][()]
            self._angle_units = decode_bytes_string(
                self._disk_chopper[SLIT_EDGES].attrs["units"]
            )
            self._slit_height_units = decode_bytes_string(
                self._disk_chopper[SLIT_HEIGHT].attrs["units"]
            )
            self._radius_units = decode_bytes_string(
                self._disk_chopper[RADIUS].attrs["units"]
            )
            self._disk_chopper[NAME][()],

        except KeyError:
            return False

        return True

    def validate_chopper(self):
        """
        Performs the following checks in order to determine if the chopper input is valid: 1) Checks that the required
        fields are present, 2) Checks that the fields have the correct type, 3) Checks that the slit edges array is 1D,
        and 4) Checks that the overall chopper geometry is valid (no overlapping slits, repeated angles, etc).
        :return: True if the chopper is valid. False otherwise.
        """
        if not (
            self.required_fields_present()
            and fields_have_correct_type(self.fields_dict)
            and edges_array_has_correct_shape(
                self.fields_dict[SLIT_EDGES].ndim, self.fields_dict[SLIT_EDGES].shape
            )
        ):
            return False

        self._chopper_details = ChopperDetails(
            self.fields_dict[SLITS],
            self.fields_dict[SLIT_EDGES],
            self.fields_dict[RADIUS],
            self.fields_dict[SLIT_HEIGHT],
            self._angle_units,
            self._slit_height_units,
            self._radius_units,
        )

        return input_describes_valid_chopper(
            self._chopper_details, self.fields_dict[SLIT_EDGES]
        )


class Point:
    """
    Basic class for representing a point with an index.
    """

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.id = None

    def set_id(self, index: int):
        """
        Give the point an ID. Attempts to make sure this can only be done once.
        """
        if self.id is not None or type(index) is not int:
            return

        self.id = index

    def point_to_qvector3d(self):
        """
        Create a QVector3D from the point.
        """
        return QVector3D(self.x, self.y, self.z)


class DiskChopperGeometryCreator:
    """
    Tool for creating OFF Geometry in the form of strings from NXdisk_chopper information.
    """

    def __init__(self, chopper_details: ChopperDetails):

        self.points = []
        self.faces = []
        self.z = 1
        self.arrow_size = 0.1
        self.resolution = 20
        self.resolution_angles = None

        self._radius = chopper_details.radius
        self._slit_edges = chopper_details.slit_edges
        self._slit_height = chopper_details.slit_height
        self._slits = chopper_details.slits

        # Create points for the front and back centres of the disk
        self.front_centre = Point(0, 0, self.z)
        self.back_centre = Point(0, 0, -self.z)

        # Add the front and back centre points to the lists of points
        self._add_point_to_list(self.front_centre)
        self._add_point_to_list(self.back_centre)

    def create_intermediate_points_and_faces(
        self,
        first_angle,
        second_angle,
        first_front,
        first_back,
        second_front,
        second_back,
        r,
    ):
        """
        Create additional points and faces between the slit edges to make the mesh look smoother.
        :param first_angle: The angle of the first slit edge in radians.
        :param second_angle: The angle of the second slit edge in radians.
        :param first_front: The front point of the first slit edge,
        :param first_back: The back point of the first slit edge.
        :param second_front: The front point of the second slit edge.
        :param second_back: The back point of the second slit edge.
        :param r: The distance between the intermediate points and the back/front centre.
        """

        # Slice the array to obtain an array of intermediate angles between the two slit edges.
        if second_angle > first_angle:
            intermediate_angles = self.resolution_angles[
                (self.resolution_angles > first_angle)
                & (self.resolution_angles < second_angle)
            ]
        else:
            # Use append rather than an or operator because the larger values need to appear first
            intermediate_angles = np.append(
                self.resolution_angles[(self.resolution_angles > first_angle)],
                self.resolution_angles[(self.resolution_angles < second_angle)],
            )
            # Add the top dead centre arrow to the file
            self.add_top_dead_centre_arrow(r)

        prev_front = first_front
        prev_back = first_back

        for angle in intermediate_angles:

            # Create the front and back points
            current_front, current_back = self.create_and_add_mirrored_points(r, angle)

            # Create a four-point face with the current points and the previous points
            self.add_face_to_list([prev_front, prev_back, current_back, current_front])

            # Create a three-point face with the two front points and the front centre point
            self.add_face_connected_to_front_centre([prev_front, current_front])

            # Create a three-point face with the two back points and the back centre point
            self.add_face_connected_to_back_centre([current_back, prev_back])
            prev_front = current_front
            prev_back = current_back

        # Create a four-point face that connects the previous two points and the points from the second slit edge
        self.add_face_to_list([prev_front, prev_back, second_back, second_front])

        # Create the final faces connected to the front and back centre points
        self.add_face_connected_to_front_centre([prev_front, second_front])
        self.add_face_connected_to_back_centre([second_back, prev_back])

    def convert_chopper_details_to_off(self):
        """
        Create an OFF file from a given chopper and user-defined thickness and resolution values.
        """
        # Find the distance from the disk centre to the bottom of the slit
        centre_to_slit_bottom = self._radius - self._slit_height

        # Create four points for the first slit in the chopper data
        point_set = self.create_and_add_point_set(
            self._radius, centre_to_slit_bottom, self._slit_edges[0], False
        )

        prev_upper_front = first_upper_front = point_set[0]
        prev_upper_back = first_upper_back = point_set[1]
        prev_lower_front = point_set[2]
        prev_lower_back = point_set[3]

        two_pi = np.pi * 2

        # Remove the first angle to avoid creating duplicate points at angle 0 and angle 360
        self.resolution_angles = np.linspace(0, two_pi, self.resolution + 1)[1:]

        for i in range(1, len(self._slit_edges)):

            # Create four points for the current slit edge
            current_upper_front, current_upper_back, current_lower_front, current_lower_back = self.create_and_add_point_set(
                self._radius, centre_to_slit_bottom, self._slit_edges[i], i % 2
            )

            # Create lower intermediate points/faces if the slit angle index is odd
            if i % 2:
                self.create_intermediate_points_and_faces(
                    self._slit_edges[i - 1],
                    self._slit_edges[i],
                    prev_lower_front,
                    prev_lower_back,
                    current_lower_front,
                    current_lower_back,
                    centre_to_slit_bottom,
                )
            # Create upper intermediate points/faces if the slit angle index is even
            else:
                self.create_intermediate_points_and_faces(
                    self._slit_edges[i - 1],
                    self._slit_edges[i],
                    prev_upper_front,
                    prev_upper_back,
                    current_upper_front,
                    current_upper_back,
                    self._radius,
                )

            prev_upper_front = current_upper_front
            prev_upper_back = current_upper_back
            prev_lower_front = current_lower_front
            prev_lower_back = current_lower_back

        # Create intermediate points/faces between the first and last slit edges
        self.create_intermediate_points_and_faces(
            self._slit_edges[-1],
            self._slit_edges[0],
            prev_upper_front,
            prev_upper_back,
            first_upper_front,
            first_upper_back,
            self._radius,
        )

    @staticmethod
    def _polar_to_cartesian_2d(r, theta):
        """
        Converts polar coordinates to cartesian coordinates.
        :param r: The vector magnitude.
        :param theta: The vector angle.
        :return: x, y
        """
        return r * np.cos(theta), r * np.sin(theta)

    def _create_mirrored_points(self, r, theta):
        """
        Creates two points that share the same x and y values and have opposite z values.
        :param r: The distance between the points and the front/back centre of the disk chopper.
        :param theta: The angle between the point and the front/back centre.
        :return: Two points that have a distance of 2*z from each other.
        """
        x, y = self._polar_to_cartesian_2d(r, theta)

        return Point(x, y, self.z), Point(x, y, -self.z)

    def create_and_add_point_set(
        self, radius, centre_to_slit_start, slit_edge, right_face
    ):
        """
        Creates and records the upper and lower points for a slit edge and adds these to the file string. Also adds the
        face made from all four points to the file string.
        :param radius: The radius of the disk chopper.
        :param centre_to_slit_start: The distance between the disk centre and the start of the slit.
        :param slit_edge: The angle of the slit in radians.
        :param: right_face: Whether or not face on the boundary of the slit edge is facing right or facing left.
        :return: A list containing point objects for the four points in the chopper mesh with an angle of `slit_edge`.
        """

        # Create the upper and lower points for the opening/closing slit edge.
        upper_front_point, upper_back_point = self._create_mirrored_points(
            radius, slit_edge
        )
        lower_front_point, lower_back_point = self._create_mirrored_points(
            centre_to_slit_start, slit_edge
        )

        # Add all of the points to the list of points.
        self._add_point_to_list(upper_front_point)
        self._add_point_to_list(upper_back_point)
        self._add_point_to_list(lower_front_point)
        self._add_point_to_list(lower_back_point)

        # Create a right-facing point list for the boundary of the slit edge.
        right_face_order = [
            lower_back_point,
            upper_back_point,
            upper_front_point,
            lower_front_point,
        ]

        if right_face:
            # Turn the points into a face if the boundary is right-facing.
            self.add_face_to_list(right_face_order)
        else:
            # Reverse the list otherwise.
            self.add_face_to_list(reversed(right_face_order))

        return [
            upper_front_point,
            upper_back_point,
            lower_front_point,
            lower_back_point,
        ]

    def create_and_add_mirrored_points(self, r, theta):
        """
        Creates and records two mirrored points and adds these to the list of points.
        :param r: The distance between the point and front/back centre of the disk chopper.
        :param theta: The angle between the point and the front/back centre.
        :return: The two point objects.
        """

        front, back = self._create_mirrored_points(r, theta)
        self._add_point_to_list(front)
        self._add_point_to_list(back)

        return front, back

    def add_face_connected_to_front_centre(self, points):
        """
        Records a face that is connected to the center point on the front of the disk chopper.
        :param points: A list of points that make up the face minus the centre point.
        """
        self.add_face_to_list([self.front_centre] + points)

    def add_face_connected_to_back_centre(self, points):
        """
        Records a face that is connected to the center point on the back of the disk chopper.
        :param points: A list of points that make up the face minus the centre point.
        """
        self.add_face_to_list([self.back_centre] + points)

    def _add_point_to_list(self, point):
        """
        Records a point and gives it an ID.
        :param point: The point that is added to the list of points.
        """
        point.set_id(len(self.points))
        self.points.append(point)

    def add_face_to_list(self, points):
        """
        Records a face by creating a list of its point IDs and adding this to `self.faces`.
        :param points: A list of the points that compose the face.
        """
        ids = [point.id for point in points]
        self.faces.append(ids)

    def add_top_dead_centre_arrow(self, r):
        """
        Adds a 2D arrow to the mesh in order to illustrate the location of the top dead centre.
        :param r: The distance between the disk centre and the top dead centre arrow.
        """
        # Create the three points that will make the arrow/triangle and add them to the list of points

        zero = 0

        arrow_points = [
            Point(*self._polar_to_cartesian_2d(r, zero), self.z),
            Point(
                *self._polar_to_cartesian_2d(r + self.arrow_size, zero),
                self.z + self.arrow_size
            ),
            Point(
                *self._polar_to_cartesian_2d(r - self.arrow_size, zero),
                self.z + self.arrow_size
            ),
        ]
        self._add_point_to_list(arrow_points[0])
        self._add_point_to_list(arrow_points[1])
        self._add_point_to_list(arrow_points[2])

        # Add the face to the list of faces
        self.add_face_to_list(arrow_points)

    def create_disk_chopper_geometry(self):
        """
        Create the string that stores all the information needed in the OFF file.
        """
        self.convert_chopper_details_to_off()

        # Add the point information to the string
        vertices = [point.point_to_qvector3d() for point in self.points]

        print(vertices)
        print(self.faces)

        return OFFGeometryNoNexus(vertices, self.faces)
