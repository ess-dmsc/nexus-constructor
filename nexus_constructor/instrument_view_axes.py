import struct

from PySide2 import QtCore
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender

from nexus_constructor.axis_colors import AxisColors
from nexus_constructor.line_geometry import LineGeometry
from nexus_constructor.qentity_utils import (
    set_material_properties,
    add_qcomponents_to_entity,
)


class InstrumentViewAxes(object):
    def __init__(self, component_root_entity, far_plane):
        """
        Class for housing the objects that create the axes in the instrument view.
        :param component_root_entity: The root entity for the instrument view components.
        :param far_plane: The far plane of the central camera. Used to determine the length of the lines.
        """

        self.component_root_entity = component_root_entity
        self.line_length = far_plane

        # The array given to the LineGeometry must be in the form [start_x, start_y, start_z, end_x, end_y, end_z].
        # All lines start at the origin for the first three elements are the same.
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

        set_material_properties(
            self.x_line_material, AxisColors.X.value, AxisColors.X.value
        )
        set_material_properties(
            self.y_line_material, AxisColors.Y.value, AxisColors.Y.value
        )
        set_material_properties(
            self.z_line_material, AxisColors.Z.value, AxisColors.Z.value
        )

        add_qcomponents_to_entity(
            self.x_line_entity, [self.x_line_mesh, self.x_line_material]
        )
        add_qcomponents_to_entity(
            self.y_line_entity, [self.y_line_mesh, self.y_line_material]
        )
        add_qcomponents_to_entity(
            self.z_line_entity, [self.z_line_mesh, self.z_line_material]
        )

    @staticmethod
    def create_data_array(line_vertices):
        """
        Takes a list with coordinates of the beginning and end of the line and converts this to a byte array.
        :param line_vertices: A list containing the start and end coordinates.
        :return: The coordinates in the form of a bytearray.
        """
        return bytearray(struct.pack("%sf" % len(line_vertices), *line_vertices))
