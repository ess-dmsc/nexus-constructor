import struct
from typing import List

from PySide6 import QtCore
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender

from nexus_constructor.instrument_view.line_geometry import LineGeometry
from nexus_constructor.instrument_view.qentity_utils import (
    create_material,
    create_qentity,
)


class InstrumentViewAxes(object):
    def __init__(self, component_root_entity: Qt3DCore.QEntity, line_length: float):
        """
        Class for housing the objects that create the axes in the instrument view.
        :param component_root_entity: The root entity for the instrument view components.
        :param line_length: The length of the line in the axes.
        """
        vertices: List = [0 for _ in range(3)]
        self.entities = []
        for i, material_name in enumerate(["x_material", "y_material", "z_material"]):
            mesh = Qt3DRender.QGeometryRenderer(component_root_entity)

            line_vertices = vertices[:]
            line_vertices[i] = line_length
            geometry = LineGeometry(
                QtCore.QByteArray(self.create_data_array(line_vertices)),
                component_root_entity,
            )

            self.set_mesh_properties(mesh, geometry)
            material, hover_material, material_family = create_material(
                material_name, component_root_entity
            )
            self.entities.append(
                create_qentity([mesh, material], component_root_entity, False)
            )
            self.entities[-1].default_material = material
            self.entities[-1].material_family = material_family

    @staticmethod
    def create_data_array(line_vertices: List[int]):
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
