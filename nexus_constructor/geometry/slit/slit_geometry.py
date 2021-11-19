from typing import List

from PySide2.QtGui import QVector3D

from nexus_constructor.common_attrs import SHAPE_GROUP_NAME
from nexus_constructor.model.geometry import OFFGeometryNoNexus


class SlitGeometry:
    def __init__(self):
        self.vertices: List[QVector3D] = []
        self.faces: List[List[int]]

        self._create_vertices()
        self._create_faces()

    def _create_vertices(self):
        half_side_length = 0.05

        coefficient_matrix = [
            [-0.5, -1, 0.1],
            [-0.1, -1, 0.1],
            [-0.5, 1, 0.1],
            [-0.1, 1, 0.1],
            [-0.5, 1, -0.1],
            [-0.1, 1, -0.1],
            [-0.5, -1, -0.1],
            [-0.1, -1, -0.1],
        ]

        # Left-rectangle
        for row, column in enumerate(coefficient_matrix):
            self.vertices.append(
                QVector3D(
                    column[0] * half_side_length,
                    column[1] * half_side_length,
                    column[2] * half_side_length,
                )
            )

        # right rectangle
        for row, column in enumerate(coefficient_matrix):
            self.vertices.append(
                QVector3D(
                    -column[0] * half_side_length,
                    -column[1] * half_side_length,
                    column[2] * half_side_length,
                )
            )

    def _create_faces(self):
        left_faces = [
            [0, 1, 3, 2],
            [2, 3, 5, 4],
            [4, 5, 7, 6],
            [6, 7, 1, 0],
            [1, 7, 5, 3],
            [6, 0, 2, 4],
        ]
        right_faces = [
            [8, 9, 11, 10],
            [10, 11, 13, 12],
            [12, 13, 15, 14],
            [14, 15, 9, 8],
            [9, 15, 13, 11],
            [14, 8, 10, 12],
        ]

        self.faces = left_faces + right_faces

    def create_slit_geometry(self) -> OFFGeometryNoNexus:
        return OFFGeometryNoNexus(self.vertices, self.faces, SHAPE_GROUP_NAME)
