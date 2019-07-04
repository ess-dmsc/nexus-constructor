import struct

from PySide2 import QtCore
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender

from nexus_constructor.axis_colors import AxisColors
from nexus_constructor.line_geometry import LineGeometry


class InstrumentViewAxes(object):
    def __init__(self, component_root_entity, far_plane):

        self.component_root_entity = component_root_entity
        self.line_length = far_plane

        origin = [0, 0, 0]
        x_line_vertices = origin + [far_plane, 0, 0]
        y_line_vertices = origin + [0, far_plane, 0]
        z_line_vertices = origin + [0, 0, far_plane]

        self.x_line_geometry = LineGeometry(
            QtCore.QByteArray(self.create_data_array(x_line_vertices))
        )
        self.y_line_geometry = LineGeometry(
            QtCore.QByteArray(self.create_data_array(y_line_vertices))
        )
        self.z_line_geometry = LineGeometry(
            QtCore.QByteArray(self.create_data_array(z_line_vertices))
        )

        self.x_line_mesh = Qt3DRender.QGeometryRenderer()
        self.y_line_mesh = Qt3DRender.QGeometryRenderer()
        self.z_line_mesh = Qt3DRender.QGeometryRenderer()

        self.x_line_mesh.setPrimitiveType(Qt3DRender.QGeometryRenderer.Lines)
        self.y_line_mesh.setPrimitiveType(Qt3DRender.QGeometryRenderer.Lines)
        self.z_line_mesh.setPrimitiveType(Qt3DRender.QGeometryRenderer.Lines)

        self.x_line_mesh.setGeometry(self.x_line_geometry)
        self.y_line_mesh.setGeometry(self.y_line_geometry)
        self.z_line_mesh.setGeometry(self.z_line_geometry)

        self.x_line_entity = Qt3DCore.QEntity(self.component_root_entity)
        self.y_line_entity = Qt3DCore.QEntity(self.component_root_entity)
        self.z_line_entity = Qt3DCore.QEntity(self.component_root_entity)

        self.x_line_material = Qt3DExtras.QPhongMaterial()
        self.y_line_material = Qt3DExtras.QPhongMaterial()
        self.z_line_material = Qt3DExtras.QPhongMaterial()

        self.x_line_material.setAmbient(AxisColors.X.value)
        self.y_line_material.setAmbient(AxisColors.Y.value)
        self.z_line_material.setAmbient(AxisColors.Z.value)

        self.x_line_material.setDiffuse(AxisColors.X.value)
        self.y_line_material.setDiffuse(AxisColors.Y.value)
        self.z_line_material.setDiffuse(AxisColors.Z.value)

        self.x_line_material.setSpecular(AxisColors.X.value)
        self.y_line_material.setSpecular(AxisColors.Y.value)
        self.z_line_material.setSpecular(AxisColors.Z.value)

        self.x_line_entity.addComponent(self.x_line_mesh)
        self.y_line_entity.addComponent(self.y_line_mesh)
        self.z_line_entity.addComponent(self.z_line_mesh)

        self.x_line_entity.addComponent(self.x_line_material)
        self.y_line_entity.addComponent(self.y_line_material)
        self.z_line_entity.addComponent(self.z_line_material)

    @staticmethod
    def create_data_array(line_vertices):
        return bytearray(struct.pack("%sf" % len(line_vertices), *line_vertices))
