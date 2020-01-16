from typing import List, Tuple
from PySide2.QtGui import QVector3D
from abc import ABC, abstractmethod
from nexus_constructor.nexus import nexus_wrapper as nx
import h5py

from nexus_constructor.nexus.validation import (
    NexusFormatError,
    ValidateDataset,
    validate_group,
)
from nexus_constructor.pixel_data import PixelMapping
from nexus_constructor.pixel_data_to_nexus_utils import (
    get_detector_faces_from_pixel_mapping,
)
from nexus_constructor.ui_utils import (
    numpy_array_to_qvector3d,
    qvector3d_to_numpy_array,
)
import numpy as np


class OFFGeometry(ABC):
    geometry_str = "OFF"

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

    @property
    @abstractmethod
    def vertices(self) -> List[QVector3D]:
        pass

    @vertices.setter
    @abstractmethod
    def vertices(self, new_vertices: List[QVector3D]):
        pass

    @property
    @abstractmethod
    def faces(self) -> List[List[int]]:
        pass

    @faces.setter
    @abstractmethod
    def faces(self, new_faces: List[List[int]]):
        pass


class OFFGeometryNoNexus(OFFGeometry):
    """
    3D mesh description of the shape of an object, based on the OFF file format.
    This class does not store its data in the NeXus file, used for placeholder shape
    for objects which have no real shape data to be stored in the file.
    """

    def __init__(self, vertices: List[QVector3D] = None, faces: List[List[int]] = None):
        """
        :param vertices: list of Vector objects used as corners of polygons in the geometry
        :param faces: list of integer lists. Each sublist is a winding path around the corners of a polygon.
            Each sublist item is an index into the vertices list to identify a specific point in 3D space
        """
        super().__init__()
        self._vertices = vertices
        self._faces = faces

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


class OFFGeometryNexus(OFFGeometry):
    """
    3D mesh description of the shape of an object, based on the OFF file format.
    http://download.nexusformat.org/sphinx/classes/base_classes/NXoff_geometry.html
    """

    def __init__(
        self,
        nexus_file: nx.NexusWrapper,
        group: h5py.Group,
        units: str = "",
        file_path: str = "",
        pixel_mapping: PixelMapping = None,
    ):
        super().__init__()
        self.file = nexus_file
        self.group = group
        self._verify_in_file()

        if pixel_mapping is not None:
            self.detector_faces = get_detector_faces_from_pixel_mapping(pixel_mapping)

        if units:
            self.units = units
        if file_path:
            self.file_path = file_path

    def _verify_in_file(self):
        """
        Check all the datasets and attributes we require are in the NXoff_geometry group
        """
        problems = validate_group(
            self.group,
            "NXoff_geometry",
            (
                ValidateDataset(
                    "vertices", shape=(None, 3), attributes={"units": None}
                ),
                ValidateDataset("winding_order"),
                ValidateDataset("faces"),
            ),
        )
        if problems:
            raise NexusFormatError("\n".join(problems))

    @property
    def detector_faces(self) -> List[int]:
        return self.file.get_field_value(self.group, "detector_faces")

    @detector_faces.setter
    def detector_faces(self, detector_faces: List[Tuple[int, int]]):
        """
        Records the detector faces in the NXoff_geometry.
        :param detector_faces: The PixelMapping object containing IDs the user provided through the Add/Edit Component window.
        """
        self.file.set_field_value(self.group, "detector_faces", detector_faces)

    @property
    def winding_order(self) -> List[int]:
        return [point for face in self.faces for point in face]

    @property
    def winding_order_indices(self) -> List[int]:
        face_sizes = [len(face) for face in self.faces]
        return [sum(face_sizes[0:i]) for i in range(len(face_sizes))]

    @property
    def off_geometry(self) -> OFFGeometry:
        return OFFGeometryNoNexus(self.vertices, self.faces)

    @property
    def vertices(self) -> List[QVector3D]:
        vertices_from_file = self.group["vertices"]
        number_of_vertices = vertices_from_file.shape[0]
        return [
            numpy_array_to_qvector3d(vertices_from_file[vertex_number][:])
            for vertex_number in range(number_of_vertices)
        ]

    @vertices.setter
    def vertices(self, new_vertices: List[QVector3D]):
        record_vertices_in_file(self.file, self.group, new_vertices)

    @property
    def faces(self) -> List[List[int]]:
        """
        Convert winding order dataset, which is a flat list for all faces,
        into a list of the vertex indices for each face
        :return: List of vertex indices for each face
        """
        winding_order_from_file = self.group["winding_order"][...]
        # Gives starting index for each face in winding_order
        face_starting_indices = self.group["faces"][...]
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
        record_faces_in_file(self.file, self.group, new_faces)

    @property
    def units(self) -> str:
        return str(self.group["cad_file_units"][...])

    @units.setter
    def units(self, units: str):
        self.file.set_field_value(
            group=self.group,
            name="cad_file_units",
            value=units,
            dtype=h5py.special_dtype(vlen=str),
        )

    @property
    def file_path(self):
        cad_file_path = "cad_file_path"
        if cad_file_path in self.group.keys():
            return str(self.group[cad_file_path][...])
        else:
            return None

    @file_path.setter
    def file_path(self, file_path: str):
        self.file.set_field_value(
            group=self.group,
            name="cad_file_path",
            value=file_path,
            dtype=h5py.special_dtype(vlen=str),
        )


def record_faces_in_file(
    nexus_wrapper: nx.NexusWrapper, group: h5py.Group, new_faces: List[List[int]]
):
    """
    Record face data in file
    :param nexus_wrapper: Wrapper for the file the data will be stored in
    :param group: The shape group node
    :param new_faces: The new face data, list of list for each face with indices of vertices in face
    """
    winding_order = [index for new_face in new_faces for index in new_face]
    nexus_wrapper.set_field_value(group, "winding_order", winding_order)
    faces_length = [0]
    faces_length.extend([len(new_face) for new_face in new_faces[:-1]])
    faces_start_indices = np.cumsum(faces_length)
    nexus_wrapper.set_field_value(group, "faces", faces_start_indices)


def record_vertices_in_file(
    nexus_wrapper: nx.NexusWrapper, group: h5py.Group, new_vertices: List[QVector3D]
):
    """
    Record vertex data in file
    :param nexus_wrapper: Wrapper for the file the data will be stored in
    :param group: The shape group node
    :param new_vertices: The new vertices data, list of cartesian coords for each vertex
    """
    vertices = [qvector3d_to_numpy_array(vertex) for vertex in new_vertices]
    vertices_node = nexus_wrapper.set_field_value(group, "vertices", vertices)
    nexus_wrapper.set_attribute_value(vertices_node, "units", "m")
