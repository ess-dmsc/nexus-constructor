from typing import List
from PySide2.QtGui import QVector3D
from abc import ABC, abstractmethod
from nexus_constructor.nexus import nexus_wrapper as nx
import h5py
from nexus_constructor.nexus.validation import (
    NexusFormatError,
    ValidateDataset,
    validate_group,
)
from nexus_constructor.ui_utils import numpy_array_to_qvector3d


class OFFGeometry(ABC):
    geometry_str = "OFF"

    @property
    @abstractmethod
    def winding_order(self):
        """
        Flattened 1D list of indices in vertices for each face
        winding_order_indices gives the start index for each face in this list
        """
        pass

    @property
    @abstractmethod
    def winding_order_indices(self):
        """
        The start index for each face in winding_order
        """
        pass

    @property
    @abstractmethod
    def off_geometry(self):
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
    Stores arbitrary 3D geometry as a list of vertices and faces, based on the Object File Format

    vertices:   list of Vector objects used as corners of polygons in the geometry
    faces:  list of integer lists. Each sublist is a winding path around the corners of a polygon. Each sublist item is
            an index into the vertices list to identify a specific point in 3D space
    """

    def __init__(self, vertices: List[QVector3D] = None, faces: List[List[int]] = None):
        self._vertices = vertices
        self._faces = faces

    @property
    def winding_order(self):
        return [point for face in self.faces for point in face]

    @property
    def winding_order_indices(self):
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
    ):
        self.file = nexus_file
        self.group = group
        self._verify_in_file()

        # Source units and file path are retained only for the purpose of populating the edit component window
        # with the options previously chosen by the user
        self.units = units
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
    def winding_order(self):
        return [point for face in self.faces for point in face]

    @property
    def winding_order_indices(self):
        face_sizes = [len(face) for face in self.faces]
        return [sum(face_sizes[0:i]) for i in range(len(face_sizes))]

    @property
    def off_geometry(self) -> OFFGeometry:
        return OFFGeometry()

    @property
    def vertices(self) -> List[QVector3D]:
        vertices_from_file = self.group["vertices"]
        number_of_vertices = vertices_from_file.shape[1]
        return [
            numpy_array_to_qvector3d(vertices_from_file[vertex_number][:])
            for vertex_number in range(number_of_vertices)
        ]

    @vertices.setter
    def vertices(self, new_vertices: List[QVector3D]):
        raise NotImplementedError

    @property
    def faces(self) -> List[List[int]]:
        winding_order_from_file = self.group["winding_order"]
        face_starting_indices = self.group["faces"]
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
        raise NotImplementedError
