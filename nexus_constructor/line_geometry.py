from PySide2 import QtCore
from PySide2.Qt3DRender import Qt3DRender


class LineGeometry(Qt3DRender.QGeometry):
    def __init__(self, vertex_data: QtCore.QByteArray, parent=None):
        """
        Geometry for depicting a line. Used for axes placed in the origin of the instrument view.
        :param vertex_data: A byte array containing the coordinates for the start and end points of the line.
        :param parent: The object parent.
        """
        Qt3DRender.QGeometry.__init__(self, parent)

        # Create a position buffer and give it the vertex data
        self.position_buffer = Qt3DRender.QBuffer(self)
        self.position_buffer.setUsage(Qt3DRender.QBuffer.StaticDraw)
        self.position_buffer.setData(vertex_data)

        # Configure a position attribute and configure it to represent a set of coordinates
        self.position_attribute = Qt3DRender.QAttribute(self)
        self.position_attribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        self.position_attribute.setVertexBaseType(Qt3DRender.QAttribute.Float)
        self.position_attribute.setVertexSize(3)
        self.position_attribute.setName(
            Qt3DRender.QAttribute.defaultPositionAttributeName()
        )
        self.position_attribute.setBuffer(self.position_buffer)

        # Set the number of points contained in the attribute
        # This must be two for the start and end of the line
        self.position_attribute.setCount(2)

        self.addAttribute(self.position_attribute)
