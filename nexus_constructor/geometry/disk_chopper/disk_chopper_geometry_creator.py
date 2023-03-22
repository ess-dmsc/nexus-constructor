from typing import List, Tuple

import numpy as np
from PySide6.QtGui import QVector3D

from nexus_constructor.common_attrs import SHAPE_GROUP_NAME
from nexus_constructor.geometry.disk_chopper.chopper_details import ChopperDetails
from nexus_constructor.model.geometry import OFFGeometryNoNexus

RESOLUTION = 20


class Point:
    """
    Basic class for representing a point with an index.
    """

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.id: int = None

    def set_id(self, index: int):
        """
        Give the point an ID. Attempts to make sure this can only be done once.
        """
        if self.id is not None or type(index) is not int:
            return

        self.id = index

    def point_to_qvector3d(self) -> QVector3D:
        """
        Create a QVector3D from the point.
        """
        return QVector3D(self.x, self.y, self.z)

    def __eq__(self, other):
        """
        Check if two points are equal. This is only used for testing.1
        :param other: The other point.
        :return: If the x, y, and z values of the points are close to each other.
        """
        diffs = [
            np.isclose(self.x, other.x),
            np.isclose(self.y, other.y),
            np.isclose(self.z, other.z),
        ]
        return all(diffs)


class DiskChopperGeometryCreator:
    """
    Tool for creating OFF Geometry in the form of strings from NXdisk_chopper information.
    """

    def __init__(self, chopper_details: ChopperDetails):
        self.points: List[Point] = []
        self.faces: List[List[int]] = []
        self.resolution = RESOLUTION
        self.resolution_angles = None

        self._radius = chopper_details.radius
        self._slit_edges = chopper_details.slit_edges
        self._slit_height = chopper_details.slit_height

        self.z = self.arrow_size = self._radius * 0.025

        # Create points for the front and back centres of the disk
        self.front_centre = Point(0, 0, self.z)
        self.back_centre = Point(0, 0, -self.z)

        # Add the front and back centre points to the lists of points
        self._add_point_to_list(self.front_centre)
        self._add_point_to_list(self.back_centre)

    @staticmethod
    def get_intermediate_angle_values_from_resolution_array(
        resolution_angles: np.ndarray, first_angle: float, second_angle: float
    ) -> np.ndarray:
        # Slice the array to obtain an array of intermediate angles between the two slit edges.
        if second_angle > first_angle:
            return resolution_angles[
                (resolution_angles > first_angle) & (resolution_angles < second_angle)
            ]

        # Use append rather than an or operator because the larger values need to appear first
        return np.append(
            resolution_angles[(resolution_angles > first_angle)],
            resolution_angles[(resolution_angles < second_angle)],
        )

    def create_cake_slice(
        self, theta: float, prev_back: Point, prev_front: Point, r: float
    ) -> Tuple[Point, Point]:
        """
        Creates the 'cake slice' shaped points/faces that make the mesh look smoother.
        :param theta: The angle of the points to be created.
        :param prev_back: The previous point that is on the 'back' of the disk chopper.
        :param prev_front: The previous point that is on the 'front' of the disk chopper.
        :param r: The length of the 'cake slice' which is either the radius or radius minus slit height.
        :return: The two new points that have been created.
        """

        # Create the current front and back points
        current_front, current_back = self.create_and_add_mirrored_points(r, theta)

        # Create a four-point face with the current points and the previous points
        self.add_face_to_list([prev_front, prev_back, current_back, current_front])

        # Create a three-point face with the two front points and the front centre point
        self.add_face_connected_to_front_centre([prev_front, current_front])

        # Create a three-point face with the two back points and the back centre point
        self.add_face_connected_to_back_centre([current_back, prev_back])

        return current_back, current_front

    def create_intermediate_points_and_faces(
        self,
        first_angle: float,
        second_angle: float,
        first_front: Point,
        first_back: Point,
        second_front: Point,
        second_back: Point,
        r: float,
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

        intermediate_angles = self.get_intermediate_angle_values_from_resolution_array(
            self.resolution_angles, first_angle, second_angle
        )

        prev_front = first_front
        prev_back = first_back

        for angle in intermediate_angles:
            current_back, current_front = self.create_cake_slice(
                angle, prev_back, prev_front, r
            )

            prev_front = current_front
            prev_back = current_back

        # Create a four-point face that connects the previous two points and the points from the second slit edge
        self.add_face_to_list([prev_front, prev_back, second_back, second_front])

        # Create the final faces connected to the front and back centre points
        self.add_face_connected_to_front_centre([prev_front, second_front])
        self.add_face_connected_to_back_centre([second_back, prev_back])

        if first_angle > second_angle:
            self.add_top_dead_centre_arrow(r)

    @staticmethod
    def create_resolution_angles(resolution: int) -> np.ndarray:
        """
        Return an array of angles where the chopper should be broken into wedges based on a resolution value.
        :param resolution: The number of angles in the array.
        :return: An array of angles in the range [0, 360).
        """

        return np.linspace(0, np.pi * 2, resolution + 1)[:-1]

    def convert_chopper_details_to_off(self):
        """
        Create an OFF file from a given chopper and user-defined thickness and resolution values.
        """
        # Find the distance from the disk centre to the bottom of the slit
        centre_to_slit_bottom = self._radius - self._slit_height

        # Create four points for the first slit in the chopper data
        (
            prev_upper_front,
            prev_upper_back,
            prev_lower_front,
            prev_lower_back,
        ) = self.create_and_add_point_set(
            self._radius, centre_to_slit_bottom, self._slit_edges[0], False
        )

        first_upper_front = prev_upper_front
        first_upper_back = prev_upper_back

        # Remove the last angle to avoid creating duplicate points at angle 0 and angle 360
        self.resolution_angles = self.create_resolution_angles(self.resolution)

        for i in range(1, len(self._slit_edges)):
            # Create four points for the current slit edge
            (
                current_upper_front,
                current_upper_back,
                current_lower_front,
                current_lower_back,
            ) = self.create_and_add_point_set(
                self._radius, centre_to_slit_bottom, self._slit_edges[i], bool(i % 2)
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
    def _polar_to_cartesian_2d(r: float, theta: float) -> Tuple[float, float]:
        """
        Converts polar coordinates to cartesian coordinates.
        :param r: The vector magnitude.
        :param theta: The vector angle.
        :return: x, y
        """
        return r * np.sin(theta), r * np.cos(theta)

    def _create_mirrored_points(self, r: float, theta: float) -> Tuple[Point, Point]:
        """
        Creates two points that share the same x and y values and have opposite z values.
        :param r: The distance between the points and the front/back centre of the disk chopper.
        :param theta: The angle between the point and the front/back centre.
        :return: Two points that have a distance of 2*z from each other.
        """
        x, y = self._polar_to_cartesian_2d(r, theta)

        return Point(x, y, self.z), Point(x, y, -self.z)

    def create_and_add_point_set(
        self,
        radius: float,
        centre_to_slit_start: float,
        slit_edge: float,
        right_facing: bool,
    ) -> List[Point]:
        """
        Creates and records the upper and lower points for a slit edge and adds these to the file string. Also adds the
        face made from all four points to the file string.
        :param radius: The radius of the disk chopper.
        :param centre_to_slit_start: The distance between the disk centre and the start of the slit.
        :param slit_edge: The angle of the slit in radians.
        :param right_facing: Whether or not face on the boundary of the slit edge is facing right or facing left.
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

        if right_facing:
            # Turn the points into a face if the boundary is right-facing.
            self.add_face_to_list(right_face_order)
        else:
            # Reverse the list otherwise.
            self.add_face_to_list(right_face_order[::-1])

        return [
            upper_front_point,
            upper_back_point,
            lower_front_point,
            lower_back_point,
        ]

    def create_and_add_mirrored_points(
        self, r: float, theta: float
    ) -> Tuple[Point, Point]:
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

    def add_face_connected_to_front_centre(self, points: List[Point]):
        """
        Records a face that is connected to the center point on the front of the disk chopper.
        :param points: A list of points that make up the face minus the centre point.
        """
        self.add_face_to_list([self.front_centre] + points)

    def add_face_connected_to_back_centre(self, points: List[Point]):
        """
        Records a face that is connected to the center point on the back of the disk chopper.
        :param points: A list of points that make up the face minus the centre point.
        """
        self.add_face_to_list([self.back_centre] + points)

    def _add_point_to_list(self, point: Point):
        """
        Records a point and gives it an ID.
        :param point: The point that is added to the list of points.
        """
        point.set_id(len(self.points))
        self.points.append(point)

    def add_face_to_list(self, points: List[Point]):
        """
        Records a face by creating a list of its point IDs and adding this to `self.faces`.
        :param points: A list of the points that compose the face.
        """
        ids = [point.id for point in points]
        self.faces.append(ids)

    def add_top_dead_centre_arrow(self, r: float):
        """
        Adds a 2D arrow to the mesh in order to illustrate the location of the top dead centre.
        :param r: The distance between the disk centre and the top dead centre arrow.
        """
        # Create the three points that will make the arrow/triangle and add them to the list of points

        zero = 0

        arrow_points = [
            Point(r, zero, self.z),
            Point(r + self.arrow_size, zero, self.z + self.arrow_size),
            Point(r - self.arrow_size, zero, self.z + self.arrow_size),
        ]

        for point in arrow_points:
            self._add_point_to_list(point)

        # Add the face to the list of faces
        self.add_face_to_list(arrow_points)

    def create_disk_chopper_geometry(self) -> OFFGeometryNoNexus:
        """
        Create the string that stores all the information needed in the OFF file.
        """
        self.convert_chopper_details_to_off()

        # Add the point information to the string
        vertices = [point.point_to_qvector3d() for point in self.points]

        return OFFGeometryNoNexus(vertices, self.faces, SHAPE_GROUP_NAME)
