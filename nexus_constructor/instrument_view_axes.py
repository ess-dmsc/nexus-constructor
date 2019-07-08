import struct
from typing import List

from PySide2 import QtCore
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DRender import Qt3DRender

from nexus_constructor.axis_colors import AxisColors
from nexus_constructor.line_geometry import LineGeometry
from nexus_constructor.qentity_utils import create_material, add_qcomponents_to_entity


class InstrumentViewAxes(object):
    def __init__(self, component_root_entity: Qt3DCore.QEntity, line_length: float):
        """
        Class for housing the objects that create the axes in the instrument view.
        :param component_root_entity: The root entity for the instrument view components.
        :param line_length: The length of the line in the axes.
        """

        self.line_entities = []
        self.line_meshes = []
        self.line_materials = []
        self.line_geometries = []

        vertices = [0 for _ in range(3)]

        for i, color in enumerate(
            [AxisColors.X.value, AxisColors.Y.value, AxisColors.Z.value]
        ):
            self.line_entities.append(Qt3DCore.QEntity(component_root_entity))
            self.line_meshes.append(Qt3DRender.QGeometryRenderer())

            line_vertices = vertices[:]
            line_vertices[i] = line_length
            self.line_geometries.append(
                LineGeometry(QtCore.QByteArray(self.create_data_array(line_vertices)))
            )

            self.set_mesh_properties(self.line_meshes[i], self.line_geometries[i])
            self.line_materials.append(create_material(color, color))
            add_qcomponents_to_entity(
                self.line_entities[i], [self.line_meshes[i], self.line_materials[i]]
            )

    @staticmethod
    def create_data_array(line_vertices: List[float]):
        """
        Takes a list with coordinates of the beginning and end of the line and converts this to a byte array.
        :param line_vertices: A list containing the start and end coordinates.
        :return: The coordinates in the form of a bytearray.
        """
        return bytearray(struct.pack("%sf" % len(line_vertices), *line_vertices))

    @staticmethod
    def set_mesh_properties(mesh: Qt3DRender.QGeometryRenderer, geometry: LineGeometry):
        """
        Set the primitive type of the mesh and provide it with a line geometry.
        :param mesh: The mesh to be configured.
        :param geometry: A LineGeometry.
        """
        mesh.setPrimitiveType(Qt3DRender.QGeometryRenderer.Lines)
        mesh.setGeometry(geometry)
