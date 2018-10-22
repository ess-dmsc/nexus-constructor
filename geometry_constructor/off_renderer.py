from geometry_constructor.data_model import OFFGeometry
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtGui import QVector3D
import struct


# Basing off a C++ custom mesh implementation at:
# https://github.com/iLya84a/qt3d/blob/master/custom-mesh-qml/CustomMesh.cpp
# and a PyQt5 example can be found at:
# https://github.com/geehalel/npindi/blob/57c092200dd9cb259ac1c730a1258a378a1a6342/apps/mount3D/world3D-starspheres.py#L86


class QtOFFGeometry(Qt3DRender.QGeometry):

    def __init__(self, model: OFFGeometry, parent=None):
        super().__init__(parent)

        # for each point in each triangle in each face, add its points to the vertices list
        vertices = []
        for face in model.faces:
            for i in range(len(face) - 2):
                for point in [face[0], face[i + 1], face[i + 2]]:
                    vertex = model.vertices[point]
                    vertices.append(vertex.x)
                    vertices.append(vertex.y)
                    vertices.append(vertex.z)

        normals = []
        for face in model.faces:
            for i in range(len(face) - 2):
                p1 = model.vertices[face[0]]
                p2 = model.vertices[face[i + 1]]
                p3 = model.vertices[face[i + 2]]
                normal = QVector3D.normal(QVector3D(p1.x, p1.y, p1.z),
                                          QVector3D(p2.x, p2.y, p2.z),
                                          QVector3D(p3.x, p3.y, p3.z))
                for j in range(3):
                    normals.append(normal.x())
                    normals.append(normal.y())
                    normals.append(normal.z())

        vertexBuffer = Qt3DRender.QBuffer(self)
        vertexBuffer.setData(
            struct.pack('%sf' % len(vertices), *vertices)
        )
        normalBuffer = Qt3DRender.QBuffer(self)
        normalBuffer.setData(
            struct.pack('%sf' % len(normals), *normals)
        )

        float_size = len(struct.pack('f', 0.0))

        positionAttribute = Qt3DRender.QAttribute(self)
        positionAttribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        positionAttribute.setBuffer(vertexBuffer)
        positionAttribute.setDataType(Qt3DRender.QAttribute.Float)
        positionAttribute.setDataSize(3)
        positionAttribute.setByteOffset(0)
        positionAttribute.setByteStride(3 * float_size)
        positionAttribute.setCount(len(vertices))
        positionAttribute.setName(Qt3DRender.QAttribute.defaultPositionAttributeName())

        normalAttribute = Qt3DRender.QAttribute(self)
        normalAttribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        normalAttribute.setBuffer(normalBuffer)
        normalAttribute.setDataType(Qt3DRender.QAttribute.Float)
        normalAttribute.setDataSize(3)
        normalAttribute.setByteOffset(0)
        normalAttribute.setByteStride(3 * float_size)
        normalAttribute.setCount(len(normals))
        normalAttribute.setName(Qt3DRender.QAttribute.defaultNormalAttributeName())

        self.addAttribute(positionAttribute)
        self.addAttribute(normalAttribute)
        self.vertex_count = len(vertices) // 3

        print('Qt mesh built')


class OffMesh(Qt3DRender.QGeometryRenderer):

    def __init__(self, geometry: OFFGeometry, parent=None):
        super().__init__(parent)

        qt_geometry = QtOFFGeometry(geometry, self)

        self.setInstanceCount(1)
        self.setFirstVertex(0)
        self.setFirstInstance(0)
        self.setPrimitiveType(Qt3DRender.QGeometryRenderer.Triangles)
        self.setGeometry(qt_geometry)
        self.setVertexCount(qt_geometry.vertex_count)
