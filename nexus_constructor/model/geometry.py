from abc import ABC, abstractmethod
from math import acos, cos, degrees, pi, sin
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PySide6.QtGui import QMatrix4x4, QVector3D

from nexus_constructor.common_attrs import (
    GEOMETRY_NX_CLASS,
    NX_BOX,
    SHAPE_GROUP_NAME,
    SHAPE_NX_CLASS,
    SIZE,
    CommonAttrs,
    CommonKeys,
)
from nexus_constructor.geometry.utils import get_an_orthogonal_unit_vector
from nexus_constructor.model.attributes import Attributes
from nexus_constructor.model.group import Group
from nexus_constructor.model.module import WriterModules, create_fw_module_object
from nexus_constructor.model.value_type import ValueTypes
from nexus_constructor.ui_utils import (
    numpy_array_to_qvector3d,
    qvector3d_to_numpy_array,
)
from nexus_constructor.unit_utils import METRES, calculate_unit_conversion_factor

WINDING_ORDER = "winding_order"
FACES = "faces"
CYLINDERS = "cylinders"
DETECTOR_NUMBER = "detector_number"
X_PIXEL_OFFSET = "x_pixel_offset"
Y_PIXEL_OFFSET = "y_pixel_offset"
Z_PIXEL_OFFSET = "z_pixel_offset"
DETECTOR_FACES = "detector_faces"


class OFFGeometry(ABC):
    _units: str = ""
    _file_path: str = ""
    _colors: List[List[int]] = []

    @property
    def units(self) -> str:
        return self._units

    @units.setter
    def units(self, units: str):
        self._units = units

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path: str):
        self._file_path = file_path

    @property
    @abstractmethod
    def winding_order(self) -> List[int]:
        """
        Flattened 1D list of indices in vertices for each face
        winding_order_indices gives the start index for each face in this list
        """
        pass

    @property
    @abstractmethod
    def winding_order_indices(self) -> List[int]:
        """
        The start index for each face in winding_order
        """
        pass

    @property
    @abstractmethod
    def off_geometry(self) -> "OFFGeometry":
        pass

    @property  # type: ignore
    @abstractmethod
    def vertices(self) -> List[QVector3D]:
        pass

    @vertices.setter  # type: ignore
    @abstractmethod
    def vertices(self, new_vertices: List[QVector3D]):
        pass

    @property  # type: ignore
    @abstractmethod
    def faces(self) -> List[List[int]]:
        pass

    @faces.setter  # type: ignore
    @abstractmethod
    def faces(self, new_faces: List[List[int]]):
        pass

    @property  # type: ignore
    @abstractmethod
    def colors(self) -> List[List[int]]:
        pass

    @colors.setter  # type: ignore
    @abstractmethod
    def colors(self, new_colors: List[List[int]]):
        pass


class OFFGeometryNoNexus(OFFGeometry, Group):
    """
    3D mesh description of the shape of an object, based on the OFF file format.
    This class does not store its data in the NeXus file, used for placeholder shape
    for objects which have no real shape data to be stored in the file.
    """

    def __init__(
        self,
        vertices: List[QVector3D] = None,
        faces: List[List[int]] = None,
        name: str = "",
        colors: List[List[int]] = [],
    ):
        """
        :param vertices: list of Vector objects used as corners of polygons in the geometry
        :param faces: list of integer lists. Each sublist is a winding path around the corners of a polygon.
            Each sublist item is an index into the vertices list to identify a specific point in 3D space
        """
        Group.__init__(self, name)
        OFFGeometry.__init__(self)
        self.name = name
        self._vertices = vertices
        self._faces = faces
        self._colors = colors

    @property
    def winding_order(self) -> List[int]:
        return [point for face in self.faces for point in face]

    @property
    def winding_order_indices(self) -> List[int]:
        face_sizes = [len(face) for face in self.faces]
        return [sum(face_sizes[0:i]) for i in range(len(face_sizes))]

    @property
    def off_geometry(self) -> OFFGeometry:
        return self

    @property
    def vertices(self) -> List[QVector3D]:
        return self._vertices

    @vertices.setter
    def vertices(self, new_vertices: List[QVector3D]):
        self._vertices = new_vertices

    @property
    def faces(self) -> List[List[int]]:
        return self._faces

    @faces.setter
    def faces(self, new_faces: List[List[int]]):
        self._faces = new_faces

    @property
    def colors(self) -> List[List[int]]:
        return self._colors

    @colors.setter
    def colors(self, new_colors: List[List[int]]):
        self._colors = new_colors


class BoxGeometry(Group):
    """
    Box geometry shape.
    """

    def __init__(
        self,
        length: float,
        width: float,
        height: float,
        name: str = "",
        units: str = "m",
    ):
        Group.__init__(self, name)
        self._size = [length, width, height]
        self._units = units
        self.nx_class = GEOMETRY_NX_CLASS
        self._create_datasets_and_add_to_shape_group()

    def _create_datasets_and_add_to_shape_group(self):
        group = Group(name=SHAPE_GROUP_NAME)
        group.nx_class = SHAPE_NX_CLASS
        group.parent_node = self
        new_child = create_fw_module_object(
            WriterModules.DATASET.value,
            self._get_dataset_config(self._size, SIZE),
            group,
        )
        new_child.type = ValueTypes.DOUBLE
        attributes = Attributes()
        attributes.set_attribute_value(CommonAttrs.UNITS, self._units)
        new_child.attributes = attributes
        new_child.parent_node = group
        group.children.append(new_child)
        group[SHAPE_GROUP_NAME] = create_fw_module_object(
            WriterModules.DATASET.value,
            self._get_dataset_config(NX_BOX, SHAPE_GROUP_NAME),
            group,
        )
        self[SHAPE_GROUP_NAME] = group

    def _get_dataset_config(self, value: Any, name: str) -> Dict:
        return {
            CommonKeys.NAME: name,
            CommonKeys.VALUES: value,
        }

    @property
    def units(self) -> str:
        return self._units

    @property
    def size(self) -> List[float]:
        return self._size

    @property
    def off_geometry(self) -> OFFGeometry:
        x = self._size[1] / 2
        y = self._size[2] / 2
        z = self._size[0] / 2
        return OFFGeometryNoNexus(
            vertices=[
                QVector3D(-x, -y, z),
                QVector3D(x, -y, z),
                QVector3D(-x, y, z),
                QVector3D(x, y, z),
                QVector3D(-x, y, -z),
                QVector3D(x, y, -z),
                QVector3D(-x, -y, -z),
                QVector3D(x, -y, -z),
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


class CylindricalGeometry(Group):
    _detector: Optional[np.array] = None

    @property
    def detector_number(self) -> List[int]:
        if self._detector is None:
            return None
        return self._detector.tolist()

    @detector_number.setter
    def detector_number(self, pixel_ids: List[int]):
        self._detector = np.array(pixel_ids)

    @property
    def units(self) -> str:
        return self[CommonAttrs.VERTICES].attributes.get_attribute_value(
            CommonAttrs.UNITS
        )

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
        return (
            numpy_array_to_qvector3d(vertices[cylinders[0], :]),
            numpy_array_to_qvector3d(vertices[cylinders[1], :]),
            numpy_array_to_qvector3d(vertices[cylinders[2], :]),
        )

    @staticmethod
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

    @property
    def cylinders(self) -> np.ndarray:
        return self.get_field_value(CYLINDERS)

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
    def off_geometry(self) -> OFFGeometry:
        steps: int = 10
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


class OFFGeometryNexus(OFFGeometry, Group):
    """
    3D mesh description of the shape of an object, based on the OFF file format.
    http://download.nexusformat.org/sphinx/classes/base_classes/NXoff_geometry.html
    """

    @property
    def detector_faces(self) -> List[Tuple[int, int]]:
        return self.get_field_value(DETECTOR_FACES).tolist()

    @detector_faces.setter
    def detector_faces(self, detector_faces: List[Tuple[int, int]]):
        """
        Records the detector faces in the NXoff_geometry as a numpy array.
        :param detector_faces: The PixelMapping object containing IDs the user provided through the Add/Edit Component window.
        """
        self.set_field_value(DETECTOR_FACES, np.array(detector_faces), ValueTypes.INT)

    @property
    def winding_order(self) -> List[int]:
        return [point for face in self.faces for point in face]

    @property
    def winding_order_indices(self) -> List[int]:
        face_sizes = [len(face) for face in self.faces]
        return [sum(face_sizes[0:i]) for i in range(len(face_sizes))]

    @property
    def off_geometry(self) -> OFFGeometry:
        return OFFGeometryNoNexus(self.vertices, self.faces, colors=self.colors)

    @property
    def vertices(self) -> List[QVector3D]:
        vertices_from_file = self.get_field_value(CommonAttrs.VERTICES)
        number_of_vertices = vertices_from_file.shape[0]
        return [
            numpy_array_to_qvector3d(vertices_from_file[vertex_number][:])
            for vertex_number in range(number_of_vertices)
        ]

    @vertices.setter
    def vertices(self, new_vertices: List[QVector3D]):
        self.record_vertices(new_vertices)

    @property
    def faces(self) -> List[List[int]]:
        """
        Convert winding order dataset, which is a flat list for all faces,
        into a list of the vertex indices for each face
        :return: List of vertex indices for each face
        """
        winding_order_from_file = self.get_field_value(WINDING_ORDER)
        # Gives starting index for each face in winding_order
        face_starting_indices = self.get_field_value(FACES)
        faces = [
            winding_order_from_file[
                face_start : face_starting_indices[index + 1]
            ].tolist()
            for index, face_start in enumerate(face_starting_indices[:-1])
        ]
        faces.append(winding_order_from_file[face_starting_indices[-1] :].tolist())
        return faces

    @faces.setter
    def faces(self, new_faces: List[List[int]]):
        self.record_faces(new_faces)

    @property
    def colors(self) -> List[List[int]]:
        return self._colors

    @colors.setter
    def colors(self, new_colors: List[List[int]]):
        self._colors = new_colors

    def record_faces(self, new_faces: List[List[int]]):
        """
        Record face data in file
        :param new_faces: The new face data, list of list for each face with indices of vertices in face
        """
        winding_order = np.array(
            [index for new_face in new_faces for index in new_face]
        )
        self.set_field_value(WINDING_ORDER, winding_order, ValueTypes.INT)
        faces_length = [0]
        faces_length.extend([len(new_face) for new_face in new_faces[:-1]])
        faces_start_indices = np.cumsum(faces_length)
        self.set_field_value(FACES, faces_start_indices, ValueTypes.INT)

    def record_vertices(self, new_vertices: List[QVector3D]):
        """
        Record vertex data in file
        :param new_vertices: The new vertices data, list of cartesian coords for each vertex
        """
        vertices = np.array(
            [qvector3d_to_numpy_array(vertex) for vertex in new_vertices]
        )
        self.set_field_value(CommonAttrs.VERTICES, vertices, ValueTypes.FLOAT)
        self[CommonAttrs.VERTICES].attributes.set_attribute_value(
            CommonAttrs.UNITS, "m"
        )


__half_side_length = 0.05
OFFCube = OFFGeometryNoNexus(
    vertices=[
        QVector3D(-__half_side_length, -__half_side_length, __half_side_length),
        QVector3D(__half_side_length, -__half_side_length, __half_side_length),
        QVector3D(-__half_side_length, __half_side_length, __half_side_length),
        QVector3D(__half_side_length, __half_side_length, __half_side_length),
        QVector3D(-__half_side_length, __half_side_length, -__half_side_length),
        QVector3D(__half_side_length, __half_side_length, -__half_side_length),
        QVector3D(-__half_side_length, -__half_side_length, -__half_side_length),
        QVector3D(__half_side_length, -__half_side_length, -__half_side_length),
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

    @property
    def cylinders(self):
        return None

    @cylinders.setter
    def cylinders(self, value):
        pass

    @property
    def detector_number(self):
        return None

    @detector_number.setter
    def detector_number(self, value):
        pass

    def __init__(self):
        pass

    @property
    def off_geometry(self) -> OFFGeometry:
        return OFFCube

    def as_dict(self, error_collector: List[str]) -> None:
        return None
