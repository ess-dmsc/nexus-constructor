from sys import platform

from PySide6 import QtCore
from PySide6.Qt3DCore import Qt3DCore
from PySide6.QtGui import QVector3D

from nexus_constructor.instrument_view.off_renderer import convert_to_bytes


class LineGeometry(Qt3DCore.QGeometry):
    q_attribute = Qt3DCore.QAttribute

    def __init__(self, vertex_data: QtCore.QByteArray, parent=None):
        """
        Geometry for depicting a line. Used for axes placed in the origin of the instrument view.
        :param vertex_data: A byte array containing the coordinates for the start and end points of the line.
        :param parent: The object parent.
        """
        Qt3DCore.QGeometry.__init__(self, parent)

        # Create a position buffer and give it the vertex data
        self.position_buffer = Qt3DCore.QBuffer(self)
        self.position_buffer.setUsage(Qt3DCore.QBuffer.StaticDraw)
        self.position_buffer.setData(vertex_data)

        # Configure a position attribute and configure it to represent a set of coordinates
        self.position_attribute = Qt3DCore.QAttribute(self)
        self.position_attribute.setAttributeType(Qt3DCore.QAttribute.VertexAttribute)
        self.position_attribute.setVertexBaseType(Qt3DCore.QAttribute.Float)
        self.position_attribute.setVertexSize(3)
        self.position_attribute.setName(
            Qt3DCore.QAttribute.defaultPositionAttributeName()
        )
        self.position_attribute.setBuffer(self.position_buffer)
        # Set the number of points contained in the attribute
        # This must be two for the start and end of the line
        self.position_attribute.setCount(2)
        self.addAttribute(self.position_attribute)

        if platform == "darwin": #  this may no longer be needed
            normal = QVector3D.normal(QVector3D(0, 0, 0), QVector3D(0, 0, 0))
            normal_buffer_values = []
            # Need to have a normal for each vector
            normal_buffer_values.extend(normal.toTuple())
            self.normal_attribute = self.create_attribute(
                normal_buffer_values, self.q_attribute.defaultNormalAttributeName()
            )
            self.addAttribute(self.normal_attribute)

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
