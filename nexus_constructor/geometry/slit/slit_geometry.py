from typing import List

from PySide2.QtGui import QVector3D

from nexus_constructor.common_attrs import SHAPE_GROUP_NAME
from nexus_constructor.model.geometry import OFFGeometryNoNexus


class SlitGeometry:
    def __init__(self):
        self.vertices: List[QVector3D]
        self.faces: List[List[int]]

        self._create_vertices()
        self._create_faces()

    def _create_vertices(self):
        half_side_length = 0.05
        self.vertices = [
            QVector3D(-2 * half_side_length, -half_side_length, half_side_length),
            QVector3D(half_side_length, -half_side_length, half_side_length),
            QVector3D(-2 * half_side_length, half_side_length, half_side_length),
            QVector3D(half_side_length, half_side_length, half_side_length),
            QVector3D(-2 * half_side_length, half_side_length, -half_side_length),
            QVector3D(half_side_length, half_side_length, -half_side_length),
            QVector3D(-half_side_length, -half_side_length, -half_side_length),
            QVector3D(half_side_length, -half_side_length, -half_side_length),
        ]
        print("vertices created")

    def _create_faces(self):
        self.faces = [
            [0, 1, 3, 2],
            [2, 3, 5, 4],
            [4, 5, 7, 6],
            [6, 7, 1, 0],
            [1, 7, 5, 3],
            [6, 0, 2, 4],
        ]
        print("faces created")

    def create_slit_geometry(self) -> OFFGeometryNoNexus:
        print("returning geometry")
        return OFFGeometryNoNexus(self.vertices, self.faces, SHAPE_GROUP_NAME)
