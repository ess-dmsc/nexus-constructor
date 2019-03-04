"""
Classes to render OFF geometries in Qt3D

Based off of a qml custom mesh example at https://github.com/iLya84a/qt3d/blob/master/custom-mesh-qml/CustomMesh.cpp
and a PyQt5 example from
https://github.com/geehalel/npindi/blob/57c092200dd9cb259ac1c730a1258a378a1a6342/apps/mount3D/world3D-starspheres.py#L86
"""

from nexus_constructor.data_model import OFFGeometry, PixelData, PixelGrid, Vector
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtGui import QVector3D
import struct
import itertools


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
    return struct.pack(f'{len(vectors)}f', *vectors)


def convert_faces_into_triangles(faces):
    """
    Converts the faces into a list of triangles
    :param faces: List of faces containing the triangles
    :return: A list of the triangles that make a face
    """
    triangles = []
    for face in faces:
        triangles_in_face = len(face) - 2
        triangles.extend([[face[0], face[i + 1], face[i + 2]] for i in range(triangles_in_face)])
    return triangles


def create_vertex_buffer(vertices, faces):
    """
    For each point in each triangle in each face, add its points to the vertices list.
    To do this we:
    Separate faces into triangles (with them starting at the 0th point)
    Get the vertices that are in the triangles
    Adding them into a flat list of points
    :param vertices: The vertices in the mesh
    :param faces: The faces in the mesh
    :return: A list of the points in the faces
    """
    triangles = convert_faces_into_triangles(faces)

    flattened_triangles = flatten(triangles)

    return flatten(vertices[point_index].xyz_list for point_index in flattened_triangles)


def create_normal_buffer(vertices, faces):
    """
    Creates normal vectors for each vertex on the mesh.
    Qt requires each vertex to have it's own normal.
    :param vertices: The vertices for the mesh
    :param faces: The faces in the mesh
    :return: A list of the normal points for the faces
    """
    triangles = convert_faces_into_triangles(faces)
    normal_buffer_values = []
    for triangle in triangles:
        # Get the vertices of each triangle
        points = [vertices[p] for p in triangle]
        # Convert our vector objects into Qt Vectors
        q_vectors = [QVector3D(*p.xyz_list) for p in points]
        # Calculate the normal, leveraging Qt
        normal = QVector3D.normal(*q_vectors)
        # Need to have a normal for each vector
        normal_buffer_values.extend(normal.toTuple() * 3)
    return normal_buffer_values


class QtOFFGeometry(Qt3DRender.QGeometry):
    """
    Builds vertex and normal buffers from arbitrary OFF geometry files that contain the faces in the geometry - these
    need to be converted to a list of triangles so they can be rendered in Qt3d by an OffMesh.
    """

    q_attribute = Qt3DRender.QAttribute

    def __init__(self, model: OFFGeometry, pixel_data: PixelData, parent=None):
        super().__init__(parent)

        if isinstance(pixel_data, PixelGrid):
            faces, vertices = self.repeat_shape_over_grid(model, pixel_data)
        else:
            faces = model.faces
            vertices = model.vertices

        vertex_buffer_values = list(create_vertex_buffer(vertices, faces))
        normal_buffer_values = create_normal_buffer(vertices, faces)

        positionAttribute = self.create_attribute(vertex_buffer_values, self.q_attribute.defaultPositionAttributeName())
        normalAttribute = self.create_attribute(normal_buffer_values, self.q_attribute.defaultNormalAttributeName())

        self.addAttribute(positionAttribute)
        self.addAttribute(normalAttribute)
        self.vertex_count = len(vertex_buffer_values) // 3

        print('Qt mesh built')

    def create_attribute(self, buffer_values, name):
        SIZE_OF_FLOAT_IN_STRUCT = 4
        POINTS_IN_VECTOR = 3

        buffer = Qt3DRender.QBuffer(self)
        buffer.setData(convert_to_bytes(buffer_values))

        attribute = self.q_attribute(self)
        attribute.setAttributeType(self.q_attribute.VertexAttribute)
        attribute.setBuffer(buffer)
        attribute.setDataSize(POINTS_IN_VECTOR)
        attribute.setByteOffset(0)
        attribute.setByteStride(POINTS_IN_VECTOR * SIZE_OF_FLOAT_IN_STRUCT)
        attribute.setCount(len(buffer_values))
        attribute.setName(name)
        return attribute

    def repeat_shape_over_grid(self, model: OFFGeometry, grid: PixelGrid):
        faces = []
        vertices = []
        for row in range(grid.rows):
            for col in range(grid.columns):
                faces += [
                    [i + (col + (row * grid.columns)) * len(model.vertices) for i in face]
                    for face in model.faces
                ]
                vertices += [
                    Vector(vec.x + (col * grid.col_width),
                           vec.y + (row * grid.row_height),
                           vec.z)
                    for vec in model.vertices
                ]
        return faces, vertices


class OffMesh(Qt3DRender.QGeometryRenderer):
    """
    An implementation of QGeometryRenderer that allows arbitrary OFF geometries to be rendered in Qt3D
    """

    def __init__(self, geometry: OFFGeometry, pixel_data: PixelData=None, parent=None):
        super().__init__(parent)

        qt_geometry = QtOFFGeometry(geometry, pixel_data, self)

        self.setInstanceCount(1)
        self.setFirstVertex(0)
        self.setFirstInstance(0)
        self.setPrimitiveType(Qt3DRender.QGeometryRenderer.Triangles)
        self.setGeometry(qt_geometry)
        self.setVertexCount(qt_geometry.vertex_count)
