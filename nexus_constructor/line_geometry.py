from PySide2 import QtCore
from PySide2.Qt3DRender import Qt3DRender
from array import array


class LineGeometry(Qt3DRender.QGeometry):
    def __init__(self, vertex_data: QtCore.QByteArray, parent=None):
        Qt3DRender.QGeometry.__init__(self, parent)
        self.m_position_buffer = Qt3DRender.QBuffer(self)
        self.m_position_buffer.setUsage(Qt3DRender.QBuffer.StaticDraw)
        self.m_position_attribute = Qt3DRender.QAttribute(self)
        self.m_position_attribute.setAttributeType(
            Qt3DRender.QAttribute.VertexAttribute
        )
        self.m_position_attribute.setDataType(Qt3DRender.QAttribute.Float)
        self.m_position_attribute.setVertexSize(3)
        self.m_position_attribute.setName(
            Qt3DRender.QAttribute.defaultPositionAttributeName()
        )
        self.m_position_attribute.setBuffer(self.m_position_buffer)
        self.addAttribute(self.m_position_attribute)
        self.add_data(vertex_data, 15)

    def add_data(self, vertex_data: QtCore.QByteArray, width: float = 0):
        # Data is a QByteArray of floats as vec3
        float_data = array("f", vertex_data.data())
        transformed_point = [
            v
            for i in range(0, len(float_data), 3)
            for v in [
                float_data[i] - width / 2.0,
                0.0,
                float_data[i + 2],
                float_data[i] + width / 2.0,
                0.0,
                float_data[i + 2],
            ]
        ]
        self.m_position_buffer.setData(
            QtCore.QByteArray(array("f", transformed_point).tobytes())
        )
        self.m_position_attribute.setCount(len(transformed_point) // 3)
