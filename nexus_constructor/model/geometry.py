from typing import List, Tuple

from PySide2.QtGui import QVector3D, QMatrix4x4

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.geometry import OFFGeometry
from nexus_constructor.model.group import Group
from nexus_constructor.ui_utils import numpy_array_to_qvector3d
import numpy as np
from math import sin, cos, pi, acos, degrees

from nexus_constructor.unit_utils import calculate_unit_conversion_factor, METRES


class CylindricalGeometry(Group):
    @property
    def detector_number(self) -> List[int]:
        return self.get_field_value("detector_number")

    @detector_number.setter
    def detector_number(self, pixel_ids: List[int]):
        self.set_field_value("detector_number", pixel_ids)

    @property
    def units(self) -> str:
        return self[CommonAttrs.VERTICES].get_attribute_value(CommonAttrs.UNITS)

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
        cylinders = self.cylinders.flatten()
        vertices = self.get_field_value(CommonAttrs.VERTICES)
        return tuple(
            numpy_array_to_qvector3d(vertices[cylinders[i], :]) for i in range(3)
        )

    @property
    def cylinders(self) -> np.ndarray:
        return self.get_field_value("cylinders")

    @property
    def radius(self) -> float:
        base_centre, base_edge, _ = self._get_cylinder_vertices()
        cylinder_radius = base_edge - base_centre
        return cylinder_radius.length()

    @property
    def axis_direction(self) -> QVector3D:
        """
        Finds the axis direction using the base centre and top centre if the height is non-zero, otherwise it just
        returns a default value of (0,0,1).
        :return: The axis direction vector.
        """
        if self.height != 0:
            base_centre, _, top_centre = self._get_cylinder_vertices()
            cylinder_axis = top_centre - base_centre
            return cylinder_axis.normalized()

        return QVector3D(0, 0, 1)

    @property
    def off_geometry(self, steps: int = 10) -> OFFGeometry:
        unit_conversion_factor = calculate_unit_conversion_factor(self.units, METRES)

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

        raise NotImplementedError

        # return OFFGeometryNoNexus(
        #     vertices=vertices, faces=rectangle_faces + top_bottom_faces
        # )

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
