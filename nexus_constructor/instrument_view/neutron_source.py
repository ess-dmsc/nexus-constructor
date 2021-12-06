from typing import List

import numpy as np
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtGui import QColor, QMatrix4x4, QVector3D

from nexus_constructor.instrument_view.qentity_utils import (
    create_material,
    create_qentity,
)


class QComponent:
    def __init__(self, root_entity) -> None:
        self.root_entity = root_entity
        self.entities: List[Qt3DCore.QEntity] = []


class NeutronSource:
    def __init__(self, root_entity=None) -> None:
        self.root_entity = root_entity
        self._source: Qt3DCore.QEntity = None
        self._neutrons: List[Qt3DCore.QEntity] = []

        self._source_length = 4
        self._source_radius = 1
        self._num_neutrons = 8
        self._neutron_offsets = self._generate_random_points_in_cylinder(
            self._num_neutrons, self._source_radius, self._source_length
        )

        self._create_neutron_source()

    def _create_neutron_source(self):
        cylinder_mesh = Qt3DExtras.QCylinderMesh(self.root_entity)
        cone_transform = Qt3DCore.QTransform(self.root_entity)
        self._set_cylinder_dimension(
            cylinder_mesh, self._source_radius, self._source_length
        )
        cone_transform.setMatrix(self._get_cylinder_transformatrion_matrix())
        material = create_material(
            QColor("blue"), QColor("lightblue"), self.root_entity, alpha=0.5
        )
        self._source = create_qentity(
            [cylinder_mesh, material, cone_transform], self.root_entity
        )
        self._setup_neutrons()

    def setParent(self, value=None):
        self._source.setParent(value)
        for neutron in self._neutrons:
            neutron.setParent(value)

    def addComponent(self, component):
        # component.setShareable(True)
        matrix = component.matrix()
        self._redo_source_transformation(component, matrix)
        self._source.addComponent(component)

        for index, neutron in enumerate(self._neutrons):
            transform = Qt3DCore.QTransform(self.root_entity)
            self._redo_neutron_transformation(
                transform, matrix, self._neutron_offsets[index]
            )
            neutron.addComponent(transform)

    def removeComponent(self, component):
        self._source.removeComponent(component)
        for neutron in self._neutrons:
            neutron.removeComponent(component)

    def _redo_source_transformation(self, transform, matrix):
        transform.setMatrix(matrix * self._get_cylinder_transformatrion_matrix())

    def _redo_neutron_transformation(self, transform, matrix, offset):
        transform.setMatrix(matrix * self._get_sphere_transformation_matrix(offset))

    def _setup_neutrons(self):
        neutron_radius = 0.1
        for i in range(self._num_neutrons):
            mesh = Qt3DExtras.QSphereMesh(self.root_entity)
            mesh.setRadius(neutron_radius)

            transform = Qt3DCore.QTransform(self.root_entity)
            transform.setMatrix(
                self._get_sphere_transformation_matrix(self._neutron_offsets[i])
            )
            neutron_material = create_material(
                QColor("black"), QColor("grey"), self.root_entity
            )
            self._neutrons.append(
                create_qentity([mesh, neutron_material, transform], self.root_entity)
            )

    def get_entity(self):
        return self._source

    @staticmethod
    def _get_sphere_transformation_matrix(offset):
        matrix = QMatrix4x4()
        matrix.translate(QVector3D(offset[0], offset[1], offset[2]))
        return matrix

    @staticmethod
    def _generate_random_points_in_cylinder(num_points, radius, height):
        offsets = []
        for _ in range(num_points):
            theta = np.random.uniform(0, 2 * np.pi)
            r = np.sqrt(np.random.uniform(0, 1)) * radius
            offsets.append(
                [
                    r * np.cos(theta),
                    r * np.sin(theta),
                    np.random.uniform(-height / 2, height / 2),
                ]
            )
        return np.array(offsets)

    @staticmethod
    def _get_cylinder_transformatrion_matrix():
        matrix = QMatrix4x4()
        matrix.rotate(90, QVector3D(1, 0, 0))
        return matrix

    @staticmethod
    def _set_cylinder_dimension(cylinder_mesh, radius, length):
        cylinder_mesh.setRadius(radius)
        cylinder_mesh.setLength(length)
