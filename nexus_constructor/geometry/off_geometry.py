from typing import List
from PySide2.QtGui import QVector3D


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
