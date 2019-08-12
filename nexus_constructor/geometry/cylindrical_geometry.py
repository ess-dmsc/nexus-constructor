from math import sin, cos, pi, acos, degrees
from typing import Tuple, List

import h5py
import numpy as np
from PySide2.QtGui import QVector3D, QMatrix4x4

from nexus_constructor.geometry.off_geometry import OFFGeometry, OFFGeometryNoNexus
from nexus_constructor.geometry.utils import get_an_orthogonal_unit_vector
from nexus_constructor.nexus import nexus_wrapper as nx
from nexus_constructor.nexus.validation import (
    NexusFormatError,
    ValidateDataset,
    validate_group,
)
from nexus_constructor.pixel_data import PixelMapping
from nexus_constructor.ui_utils import (
    numpy_array_to_qvector3d,
    qvector3d_to_numpy_array,
)
from nexus_constructor.unit_converter import calculate_unit_conversion_factor


def calculate_vertices(
    axis_direction: QVector3D, height: float, radius: float
) -> np.ndarray:
    """
    Given cylinder axis, height and radius, calculate the base centre, base edge and top centre vertices
    :param axis_direction: axis of the cylinder (not required to be unit vector)
    :param height: height of the cylinder
    :param radius: radius of the cylinder
    :return: base centre, base edge and top centre vertices as a numpy array
    """
    axis_direction = axis_direction.normalized()
    top_centre = axis_direction * height / 2.0
    base_centre = axis_direction * height / -2.0
    radial_direction = get_an_orthogonal_unit_vector(axis_direction).normalized()
    base_edge = base_centre + (radius * radial_direction)
    vertices = np.vstack(
        (
            qvector3d_to_numpy_array(base_centre),
            qvector3d_to_numpy_array(base_edge),
            qvector3d_to_numpy_array(top_centre),
        )
    )
    return vertices


class CylindricalGeometry:
    """
    Describes the shape of a cylinder in 3D space. The cylinder's centre is the origin of the local coordinate system.
    This wrapper does not have setters, delete cylinder and create a new one if the cylinder needs to change.

    Note, the NXcylindrical_geometry group can describe multiple cylinders, but here we are using it only for one.
    """

    geometry_str = "Cylinder"

    def __init__(
        self,
        nexus_file: nx.NexusWrapper,
        group: h5py.Group,
        pixel_mapping: PixelMapping = None,
    ):
        self.file = nexus_file
        self.group = group
        self._verify_in_file()

        if pixel_mapping is not None:
            self.record_detector_number(pixel_mapping.pixel_ids)

    def _verify_in_file(self):
        """
        Check all the datasets and attributes we require are in the NXcylindrical_geometry group
        """
        problems = validate_group(
            self.group,
            "NXcylindrical_geometry",
            (
                ValidateDataset(
                    "vertices", shape=(None, 3), attributes={"units": None}
                ),
                ValidateDataset("cylinders"),
            ),
        )
        if problems:
            raise NexusFormatError("\n".join(problems))

    def record_detector_number(self, detector_ids: List[int]):
        self.file.set_field_value(
            self.group,
            "detector_number",
            np.array([i for i in detector_ids if i is not None]),
            dtype="int64",
        )

    @property
    def detector_number(self) -> List[int]:
        return self.file.get_field_value(self.group, "detector_number")

    @detector_number.setter
    def detector_number(self, pixel_mapping: PixelMapping):
        self.file.set_field_value(self.group, "detector_number", pixel_mapping.pixel_ids)

    @property
    def units(self) -> str:
        return str(self.group["vertices"].attrs["units"])

    @property
    def height(self) -> float:
        base_centre, _, top_centre = self._get_cylinder_vertices()
        cylinder_axis = top_centre - base_centre
        return cylinder_axis.length()

    def _get_cylinder_vertices(self) -> Tuple[QVector3D, QVector3D, QVector3D]:
        """
        Get the three points defining the cylinder
        We define "base" as the end of the cylinder in the -ve axis direction
        :return: base centre point, base edge point, top centre point
        """
        # flatten cylinders in case there are multiple cylinders defined, we'll take the first three elements,
        # so effectively any cylinder after the first one is ignored
        cylinders = self.file.get_field_value(self.group, "cylinders").flatten()
        vertices = self.file.get_field_value(self.group, "vertices")
        return tuple(
            numpy_array_to_qvector3d(vertices[cylinders[i], :]) for i in range(3)
        )

    @property
    def radius(self) -> float:
        base_centre, base_edge, _ = self._get_cylinder_vertices()
        cylinder_radius = base_edge - base_centre
        return cylinder_radius.length()

    @property
    def axis_direction(self) -> QVector3D:
        base_centre, _, top_centre = self._get_cylinder_vertices()
        cylinder_axis = top_centre - base_centre
        return cylinder_axis.normalized()

    @property
    def off_geometry(self, steps: int = 20) -> OFFGeometry:
        unit_conversion_factor = calculate_unit_conversion_factor(self.units)

        # A list of vertices describing the circle at the bottom of the cylinder
        bottom_circle = [
            QVector3D(sin(2 * pi * i / steps), cos(2 * pi * i / steps), 0) * self.radius
            for i in range(steps)
        ]

        # The top of the cylinder is the bottom shifted upwards
        top_circle = [vector + QVector3D(0, 0, self.height) for vector in bottom_circle]

        # The true cylinder are all vertices from the unit cylinder multiplied by the conversion factor
        vertices = [
            vector * unit_conversion_factor for vector in bottom_circle + top_circle
        ]

        # rotate each vertex to produce the desired cylinder mesh
        rotate_matrix = self._rotation_matrix()
        vertices = [vector * rotate_matrix for vector in vertices]

        def vertex_above(vertex):
            """
            Returns the index of the vertex above this one in the cylinder.
            """
            return vertex + steps

        def next_vertex(vertex):
            """
            Returns the next vertex around in the top or bottom circle of the cylinder.
            """
            return (vertex + 1) % steps

        # Rectangular faces joining the top and bottom
        rectangle_faces = [
            [i, vertex_above(i), vertex_above(next_vertex(i)), next_vertex(i)]
            for i in range(steps)
        ]

        # Step sided shapes describing the top and bottom
        # The bottom uses steps of -1 to preserve winding order
        top_bottom_faces = [
            [i for i in range(steps)],
            [i for i in range((2 * steps) - 1, steps - 1, -1)],
        ]

        return OFFGeometryNoNexus(
            vertices=vertices, faces=rectangle_faces + top_bottom_faces
        )

    def _rotation_matrix(self) -> QMatrix4x4:
        """
        :return: A QMatrix4x4 describing the rotation from the Z axis to the cylinder's axis
        """
        default_axis = QVector3D(0, 0, 1)
        desired_axis = self.axis_direction.normalized()
        rotate_axis = QVector3D.crossProduct(desired_axis, default_axis)
        rotate_radians = acos(QVector3D.dotProduct(desired_axis, default_axis))
        rotate_matrix = QMatrix4x4()
        rotate_matrix.rotate(degrees(rotate_radians), rotate_axis)
        return rotate_matrix
