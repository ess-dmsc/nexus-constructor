from PySide2.QtGui import QVector3D, QMatrix4x4
from nexus_constructor.unit_converter import calculate_unit_conversion_factor
from math import sin, cos, pi, acos, degrees
import h5py
import numpy as np
from nexus_constructor.nexus import nexus_wrapper as nx
from nexus_constructor.nexus.validation import (
    NexusFormatError,
    ValidateDataset,
    validate_group,
)
from nexus_constructor.ui_utils import (
    numpy_array_to_qvector3d,
    qvector3d_to_numpy_array,
)
from typing import List, TypeVar, Tuple


# Temporary method here until the one above is no longer needed
def validate_nonzero_qvector(value: QVector3D):
    if value.x() == 0 and value.y() == 0 and value.z() == 0:
        raise ValueError("Vector is zero length")


def _get_an_orthogonal_unit_vector(input_vector: QVector3D):
    """
    Return a unit vector which is orthogonal to the input vector
    There are infinite valid solutions, just one is returned
    """
    if np.abs(input_vector.z()) < np.abs(input_vector.x()):
        vector = QVector3D(input_vector.x(), -input_vector.y(), 0.0)
        return vector.normalized()
    vector = QVector3D(0.0, -input_vector.z(), input_vector.y())
    return vector.normalized()


class OFFGeometry:
    """
    Stores arbitrary 3D geometry as a list of vertices and faces, based on the Object File Format

    vertices:   list of Vector objects used as corners of polygons in the geometry
    faces:  list of integer lists. Each sublist is a winding path around the corners of a polygon. Each sublist item is
            an index into the vertices list to identify a specific point in 3D space
    """

    geometry_str = "OFF"

    def __init__(
        self,
        vertices: List[QVector3D] = None,
        faces: List[List[int]] = None,
        units: str = "",
        file_path: str = "",
    ):
        self.vertices = vertices
        self.faces = faces

        # Source units and file path are retained only for the purpose of populating the edit component window
        # with the options previously chosen by the user
        self.units = units
        self.file_path = file_path

    @property
    def winding_order(self):
        return [point for face in self.faces for point in face]

    @property
    def winding_order_indices(self):
        face_sizes = [len(face) for face in self.faces]
        return [sum(face_sizes[0:i]) for i in range(len(face_sizes))]

    @property
    def off_geometry(self):
        return self


OFFCube = OFFGeometry(
    vertices=[
        QVector3D(-0.5, -0.5, 0.5),
        QVector3D(0.5, -0.5, 0.5),
        QVector3D(-0.5, 0.5, 0.5),
        QVector3D(0.5, 0.5, 0.5),
        QVector3D(-0.5, 0.5, -0.5),
        QVector3D(0.5, 0.5, -0.5),
        QVector3D(-0.5, -0.5, -0.5),
        QVector3D(0.5, -0.5, -0.5),
    ],
    faces=[
        [0, 1, 3, 2],
        [2, 3, 5, 4],
        [4, 5, 7, 6],
        [6, 7, 1, 0],
        [1, 7, 5, 3],
        [6, 0, 2, 4],
    ],
)


class NoShapeGeometry:
    """
    Dummy object for components with no geometry.
    """

    geometry_str = "None"

    def __init__(self):
        pass

    @property
    def off_geometry(self):
        return OFFCube


class CylindricalGeometry:
    """
    Describes the shape of a cylinder in 3D space. The cylinder's centre is the origin of the local coordinate system.

    Note, the NXcylindrical_geometry group can describe multiple cylinders, but here we are using it only for one.
    """

    geometry_str = "Cylinder"

    def __init__(self, nexus_file: nx.NexusWrapper, group: h5py.Group):
        self.file = nexus_file
        self.group = group
        self._verify_in_file()

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
                ValidateDataset("cylinders", (None, 3)),
            ),
        )
        if problems:
            raise NexusFormatError("\n".join(problems))

    @property
    def units(self) -> str:
        return str(self.group["vertices"].attrs["units"])

    @units.setter
    def units(self, new_units: str):
        self.group["vertices"].attrs["units"] = new_units

    @property
    def height(self) -> float:
        base_centre, _, top_centre = self._get_cylinder_vertices()
        cylinder_axis = top_centre - base_centre
        return cylinder_axis.length()

    @height.setter
    def height(self, new_height: float):
        old_base_centre, old_base_edge, old_top_centre = self._get_cylinder_vertices()
        cylinder_axis = old_top_centre - old_base_centre
        old_height = cylinder_axis.length()
        half_height_change = 0.5 * (new_height - old_height) * self.axis_direction
        new_base_centre = qvector3d_to_numpy_array(old_base_centre - half_height_change)
        new_base_edge = qvector3d_to_numpy_array(old_base_edge - half_height_change)
        new_top_centre = qvector3d_to_numpy_array(old_top_centre + half_height_change)
        vertices = np.vstack((new_base_centre, new_base_edge, new_top_centre))
        cylinders = np.array([0, 1, 2])
        self.file.set_field_value(self.group, "cylinders", cylinders)
        self.file.set_field_value(self.group, "vertices", vertices)

    def _get_cylinder_vertices(self) -> Tuple[QVector3D, QVector3D, QVector3D]:
        """
        Get the three points defining the cylinder
        We define "base" as the end of the cylinder in the -ve axis direction
        :return: base centre point, base edge point, top centre point
        """
        cylinders = self.file.get_field_value(self.group, "cylinders")
        cylinder = cylinders[0]  # We will only deal with the first cylinder
        vertices = self.file.get_field_value(self.group, "vertices")
        base_centre = numpy_array_to_qvector3d(vertices[cylinder[0], :])
        base_edge = numpy_array_to_qvector3d(vertices[cylinder[1], :])
        top_centre = numpy_array_to_qvector3d(vertices[cylinder[2], :])
        return base_centre, base_edge, top_centre

    @property
    def radius(self) -> float:
        base_centre, base_edge, _ = self._get_cylinder_vertices()
        cylinder_radius = base_edge - base_centre
        return cylinder_radius.length()

    @radius.setter
    def radius(self, new_radius: float):
        base_centre, base_edge, _ = self._get_cylinder_vertices()
        cylinder_radius = base_edge - base_centre
        new_cylinder_radius = qvector3d_to_numpy_array(
            cylinder_radius.normalized() * new_radius
        )
        vertices = self.file.get_field_value(self.group, "vertices")
        vertices[1, :] = new_cylinder_radius
        self.file.set_field_value(self.group, "vertices", vertices)

    @property
    def axis_direction(self) -> QVector3D:
        base_centre, _, top_centre = self._get_cylinder_vertices()
        cylinder_axis = top_centre - base_centre
        return cylinder_axis.normalized()

    @axis_direction.setter
    def axis_direction(self, new_axis_direction: QVector3D):
        """
        Not required to be a unit vector, but must be non-zero
        :param new_axis_direction: Vector describing direction of the cylinder's axis
        """
        validate_nonzero_qvector(new_axis_direction)
        # TODO rotate the vertices by the angle between the new and old axis directions
        raise NotImplementedError()

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

        return OFFGeometry(vertices=vertices, faces=rectangle_faces + top_bottom_faces)

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
