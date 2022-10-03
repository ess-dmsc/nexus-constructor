"""
Classes to render OFF geometries in Qt3D

Based off of a qml custom mesh example at https://github.com/iLya84a/qt3d/blob/master/custom-mesh-qml/CustomMesh.cpp
and a PyQt5 example from
https://github.com/geehalel/npindi/blob/57c092200dd9cb259ac1c730a1258a378a1a6342/apps/mount3D/world3D-starspheres.py#L86
"""
import itertools
import struct
from typing import List, Tuple

import numpy as np
import open3d as o3d
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtGui import QVector3D

from nexus_constructor.model.geometry import OFFGeometry
from nexus_constructor.ui_utils import ProgressBar


def flatten(list_to_flatten):
    """
    Flattens a list of lists into a single list
    :param list_to_flatten: The list of lists
    :return: A single list containing all values
    """
    return itertools.chain.from_iterable(list_to_flatten)


def convert_to_bytes(vectors):
    """
    Converts a list of vectors into the byte format required by Qt
    :param vectors: The list of vectors to convert
    :return: The byte representation
    """
    return struct.pack(f"{len(vectors)}f", *vectors)


def convert_faces_into_triangles(faces, progress_bar: ProgressBar = None):
    """
    Converts the faces into a list of triangles
    :param faces: List of faces containing the triangles
    :param progress_bar: optional parameter progress bar.
    :return: A list of the triangles that make a face
    """
    triangles = []
    for face in faces:
        if progress_bar:
            progress_bar.update_progress_bar()
        triangles_in_face = len(face) - 2
        triangles.extend(
            [[face[0], face[i + 1], face[i + 2]] for i in range(triangles_in_face)]
        )
    return triangles


def create_vertex_buffer(vertices, triangles):
    """
    For each point in each triangle in each face, add its points to the vertices list.
    To do this we:
    Separate faces into triangles (with them starting at the 0th point)
    Get the vertices that are in the triangles
    Adding them into a flat list of points
    :param vertices: The vertices in the mesh
    :param triangles: A list of the triangles that make up each face in the mesh
    :return: A list of the points in the faces
    """
    flattened_triangles = flatten(triangles)

    return flatten(
        vertices[point_index].toTuple() for point_index in flattened_triangles
    )


def create_normal_buffer(vertices, triangles, progress_bar: ProgressBar = None):
    """
    Creates normal vectors for each vertex on the mesh.
    Qt requires each vertex to have it's own normal.
    :param vertices: The vertices for the mesh
    :param triangles: A list of the triangles that make up each face in the mesh
    :param progress_bar: optional parameter progress bar.
    :return: A list of the normal points for the faces
    """
    normal_buffer_values = []
    for triangle in triangles:
        if progress_bar:
            progress_bar.update_progress_bar()
        # Get the vertices of each triangle
        points = [vertices[p] for p in triangle]
        # Convert our vector objects into Qt Vectors
        # Calculate the normal, leveraging Qt
        normal = QVector3D.normal(*points)
        # Need to have a normal for each vector
        normal_buffer_values.extend(normal.toTuple() * 3)
    return normal_buffer_values


def create_color_buffer(vertex_count, colors, progress_bar: ProgressBar = None):
    """
    Creates a color for each face in the mesh.
    :param vertex_count: The vertex count.
    :param colors: The colors for the mesh
    :param progress_bar: optional parameter progress bar.
    :return: A list of the colors for the faces
    """
    color_buffer_values: List[int] = []
    if not colors:
        return color_buffer_values
    repeat_color = int(vertex_count / len(colors))
    for color in colors:
        if progress_bar:
            progress_bar.update_progress_bar()
        color_buffer_values.extend(color * repeat_color)
    return color_buffer_values


def repeat_shape_over_positions(
    model: OFFGeometry, positions: List[QVector3D]
) -> Tuple[List[List[int]], List[QVector3D]]:
    faces = []
    vertices = []
    for i, position in enumerate(positions):
        vertices.extend([vertex + position for vertex in model.vertices])
        faces.extend(
            [
                [vertex + i * len(model.vertices) for vertex in face]
                for face in model.faces
            ]
        )
    return faces, vertices


def vertri_to_verfacwin(vertices, triangles):
    new_vertices = []
    new_faces = []
    winding_order = []
    face_ind = 0
    for triangle in triangles:
        new_faces.append(face_ind)
        for ind in triangle:
            face_ind += 1
            winding_order.append(ind)
            new_vertices.append(vertices[ind])
    return new_vertices, new_faces, winding_order


class QtOFFGeometry(Qt3DCore.QGeometry):
    """
    Builds vertex and normal buffers from arbitrary OFF geometry files that contain the faces in the geometry - these
    need to be converted to a list of triangles so they can be rendered in Qt3d by an OffMesh.
    """

    q_attribute = Qt3DCore.QAttribute

    def __init__(
        self,
        model: OFFGeometry,
        positions: List[QVector3D] = None,
        parent=None,
        use_progress_bar: bool = False,
        allow_simplification: bool = True,
    ):
        """
        Creates the geometry for the OFF to be displayed in Qt3D.
        :param model: The geometry to render
        :param positions: The posit
        :param parent: A list of positions to copy the mesh into. If None specified a single mesh is
        produced at the origin.
        """
        super().__init__(parent)

        self.has_simplified_geometry = False

        if positions is None:
            positions = [QVector3D(0, 0, 0)]

        faces, vertices = repeat_shape_over_positions(model, positions)

        triangles = convert_faces_into_triangles(
            faces,
            ProgressBar(len(faces), "Shape conversion progress")
            if use_progress_bar
            else None,
        )

        if len(triangles) > 100000 and allow_simplification:
            print("Simplifying mesh")
            temp_mesh = o3d.geometry.TriangleMesh()

            temp_mesh.vertices = o3d.utility.Vector3dVector(
                np.array([np.asarray(v.toTuple()) for v in vertices])
            )
            temp_mesh.triangles = o3d.utility.Vector3iVector(
                np.array([np.asarray(t) for t in triangles]).astype(np.int32)
            )

            simplified_mesh, _ = temp_mesh.compute_convex_hull()
            simplified_mesh.compute_vertex_normals()

            new_vertices = np.asarray(simplified_mesh.vertices)
            new_triangles = np.asarray(simplified_mesh.triangles)

            vertices = [QVector3D(*list(v)) for v in new_vertices]
            triangles = [list(t) for t in new_triangles]
            self.has_simplified_geometry = True
            self.simple_geometry = vertices, triangles

        vertex_buffer_values = list(create_vertex_buffer(vertices, triangles))
        self.vertex_count = len(vertex_buffer_values) // 3
        normal_buffer_values = create_normal_buffer(
            vertices,
            triangles,
            ProgressBar(len(triangles), "Vector buffer creation")
            if use_progress_bar
            else None,
        )
        color_buffer_values = create_color_buffer(
            self.vertex_count,
            model.colors,
            ProgressBar(len(model.colors), "Material creation")
            if use_progress_bar
            else None,
        )
        positionAttribute = self.create_attribute(
            vertex_buffer_values, self.q_attribute.defaultPositionAttributeName()
        )
        self.addAttribute(positionAttribute)
        normalAttribute = self.create_attribute(
            normal_buffer_values, self.q_attribute.defaultNormalAttributeName()
        )
        self.addAttribute(normalAttribute)
        if model.colors:
            colorAttribute = self.create_attribute(
                color_buffer_values, self.q_attribute.defaultColorAttributeName()
            )
            self.addAttribute(colorAttribute)

    def create_attribute(self, buffer_values, name):
        SIZE_OF_FLOAT_IN_STRUCT = 4
        POINTS_IN_VECTOR = 3

        buffer = Qt3DCore.QBuffer(self)
        buffer.setData(convert_to_bytes(buffer_values))

        attribute = self.q_attribute(self)
        attribute.setAttributeType(self.q_attribute.VertexAttribute)
        attribute.setBuffer(buffer)
        attribute.setVertexSize(POINTS_IN_VECTOR)
        attribute.setByteOffset(0)
        attribute.setByteStride(POINTS_IN_VECTOR * SIZE_OF_FLOAT_IN_STRUCT)
        attribute.setCount(len(buffer_values))
        attribute.setName(name)
        return attribute


class OffMesh(Qt3DRender.QGeometryRenderer):
    """
    An implementation of QGeometryRenderer that allows arbitrary OFF geometries to be rendered in Qt3D
    """

    def __init__(
        self,
        geometry: OFFGeometry,
        parent: Qt3DCore.QEntity,
        positions: List[QVector3D] = None,
        use_progress_bar: bool = False,
        allow_simplification: bool = True,
    ):
        """
        Creates a geometry renderer for OFF geometry.
        :param geometry: The geometry to render
        :param parent: The parent entity to attach the mesh to.
        :param positions: A list of positions to copy the mesh into. If None specified a single mesh is
        produced at the origin.
        """
        super().__init__(parent)

        self.setInstanceCount(1)
        self.qt_geometry = QtOFFGeometry(
            geometry, positions, self, use_progress_bar, allow_simplification
        )
        self.setVertexCount(self.qt_geometry.vertex_count)
        self.setFirstVertex(0)
        self.setPrimitiveType(Qt3DRender.QGeometryRenderer.Triangles)
        self.setFirstInstance(0)
        self.setGeometry(self.qt_geometry)
        self.simple_geometry = None
        if self.qt_geometry.has_simplified_geometry:
            self.simple_geometry = self.qt_geometry.simple_geometry
