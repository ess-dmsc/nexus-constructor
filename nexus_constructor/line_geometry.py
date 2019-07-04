from PySide2 import QtCore
from PySide2.Qt3DRender import Qt3DRender


class LineGeometry(Qt3DRender.QGeometry):
    def __init__(self, vertex_data: QtCore.QByteArray, parent=None):
        Qt3DRender.QGeometry.__init__(self, parent)
        self.m_position_buffer = Qt3DRender.QBuffer(self)
        self.m_position_buffer.setUsage(Qt3DRender.QBuffer.StaticDraw)
        self.m_position_attribute = Qt3DRender.QAttribute(self)
        self.m_position_attribute.setAttributeType(
            Qt3DRender.QAttribute.VertexAttribute
        )
        self.m_position_attribute.setVertexBaseType(Qt3DRender.QAttribute.Float)
        self.m_position_attribute.setVertexSize(3)
        self.m_position_attribute.setName(
            Qt3DRender.QAttribute.defaultPositionAttributeName()
        )
        self.m_position_attribute.setBuffer(self.m_position_buffer)
        self.addAttribute(self.m_position_attribute)
        self.m_position_buffer.setData(vertex_data)
        self.m_position_attribute.setCount(2)
