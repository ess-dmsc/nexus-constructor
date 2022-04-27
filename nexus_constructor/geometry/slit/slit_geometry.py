from typing import List

from PySide2.QtGui import QVector3D

from nexus_constructor.common_attrs import SHAPE_GROUP_NAME
from nexus_constructor.model.geometry import OFFGeometryNoNexus


class SlitGeometry:
    def __init__(self, gaps: tuple):
        self.vertices: List[QVector3D] = []
        self.faces: List[List[int]]
        self._gaps: tuple = gaps
        self._create_vertices()
        self._create_faces()

    def _create_vertices(self):
        half_side_length = 0.05
        x_gap, y_gap = self._gaps
        dy = half_side_length

        if x_gap:
            x_1 = 0.0
            x_2 = -1.0
            dx = x_gap / 2 + half_side_length
        else:
            x_1 = -0.1
            x_2 = -0.5
            dx = 0
        if y_gap:
            dy = y_gap / 2

        slit_matrix = [
            [x_2, -1, 0.1],
            [x_1, -1, 0.1],
            [x_2, 1, 0.1],
            [x_1, 1, 0.1],
            [x_2, 1, -0.1],
            [x_1, 1, -0.1],
            [x_2, -1, -0.1],
            [x_1, -1, -0.1],
        ]
        # Left and right rectangle.
        dimension_matrix = []
        for column in slit_matrix:
            dimension_matrix.append(
                [
                    column[0] * half_side_length + dx,
                    column[1] * dy,
                    column[2] * half_side_length,
                ]
            )
        vertices_left_bank: List[QVector3D] = []
        vertices_right_bank: List[QVector3D] = []
        for column in dimension_matrix:
            vertices_left_bank.append(QVector3D(column[0], column[1], column[2]))
            vertices_right_bank.append(QVector3D(-column[0], -column[1], column[2]))

        # Lower and upper rectangle.
        slit_thickness = 0.02
        x_dist = dx if x_gap else half_side_length / 2
        slit_matrix = [
            [1, dy, 0.1],
            [-1, dy, 0.1],
            [1, slit_thickness + dy, 0.1],
            [-1, slit_thickness + dy, 0.1],
            [1, slit_thickness + dy, -0.1],
            [-1, slit_thickness + dy, -0.1],
            [1, dy, -0.1],
            [-1, dy, -0.1],
        ]
        dimension_matrix = []
        for column in slit_matrix:
            dimension_matrix.append(
                [column[0] * x_dist, column[1], column[2] * half_side_length]
            )
        vertices_lower_bank: List[QVector3D] = []
        vertices_upper_bank: List[QVector3D] = []
        for column in dimension_matrix:
            vertices_lower_bank.append(QVector3D(column[0], column[1], column[2]))
            vertices_upper_bank.append(QVector3D(column[0], -column[1], column[2]))
        self.vertices = (
            vertices_left_bank
            + vertices_right_bank
            + vertices_lower_bank
            + vertices_upper_bank
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
            [col[0] + 8, col[1] + 8, col[2] + 8, col[3] + 8] for col in left_faces
        ]
        lower_faces = [
            [col[0] + 8, col[1] + 8, col[2] + 8, col[3] + 8] for col in right_faces
        ]
        upper_faces = [
            [col[0] + 8, col[1] + 8, col[2] + 8, col[3] + 8] for col in lower_faces
        ]
        self.faces = left_faces + right_faces + lower_faces + upper_faces

    def create_slit_geometry(self) -> OFFGeometryNoNexus:
        return OFFGeometryNoNexus(self.vertices, self.faces, SHAPE_GROUP_NAME)
