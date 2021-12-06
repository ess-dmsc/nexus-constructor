from typing import List

import numpy as np
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtGui import QColor, QMatrix4x4, QVector3D

from nexus_constructor.instrument_view.qentity_utils import (
    MATERIAL_ALPHA,
    MATERIAL_COLORS,
    MATERIAL_DIFFUSE_COLORS,
    create_material,
    create_qentity,
)


class QComponent:
    def __init__(self, root_entity, nx_class):
        self.root_entity = root_entity
        self.nx_class = nx_class

        self.entities: List[Qt3DCore.QEntity] = []
        self.default_material = self._create_default_material()

    def create_entities(self):
        raise NotImplementedError

    def add_transformation(self, transformation):
        raise NotImplementedError

    def remove_transformation(self, transformation):
        for entity in self.entities:
            entity.removeComponent(transformation)

    def setParent(self, value=None):
        for entity in self.entities:
            entity.setParent(value)

    def get_entity(self):
        return self.entities[0]

    def _create_default_material(self):
        return create_material(
            MATERIAL_COLORS.get(self.nx_class, QColor("black")),
            MATERIAL_DIFFUSE_COLORS.get(self.nx_class, QColor("grey")),
            self.root_entity,
            MATERIAL_ALPHA.get(self.nx_class),
        )


class OffMeshQComponent(QComponent):
    def __init__(self, mesh, root_entity, nx_class):
        super().__init__(root_entity, nx_class)
        self._mesh = mesh

    def create_entities(self):
        self.entities.append(
            create_qentity([self._mesh, self.default_material], self.root_entity)
        )

    def add_transformation(self, transformation):
        self.entities[0].addComponent(transformation)


class NeutronSource(QComponent):
    def __init__(self, root_entity, nx_class):
        super().__init__(root_entity, nx_class)
        self._source_length = 4
        self._source_radius = 1
        self._num_neutrons = 8
        self._neutron_offsets = self._generate_random_points_in_cylinder(
            self._num_neutrons, self._source_radius, self._source_length
        )

    def create_entities(self):
        self._create_source()
        self._setup_neutrons()

    def add_transformation(self, transformation):
        matrix = transformation.matrix()
        for index, entity in enumerate(self.entities):
            if index == 0:  # source
                self._redo_source_transformation(transformation, matrix)
                entity.addComponent(transformation)
            else:  # neutrons
                transform = Qt3DCore.QTransform(self.root_entity)
                self._redo_neutron_transformation(
                    transform, matrix, self._neutron_offsets[index - 1]
                )
                entity.addComponent(transform)

    def _create_source(self):
        cylinder_mesh = Qt3DExtras.QCylinderMesh(self.root_entity)
        cone_transform = Qt3DCore.QTransform(self.root_entity)
        self._set_cylinder_dimension(
            cylinder_mesh, self._source_radius, self._source_length
        )
        cone_transform.setMatrix(self._get_cylinder_transformatrion_matrix())

        self.entities.append(
            create_qentity(
                [cylinder_mesh, self.default_material, cone_transform], self.root_entity
            )
        )

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
            entity = create_qentity(
                [mesh, neutron_material, transform], self.root_entity
            )
            self.entities.append(entity)

    def _redo_source_transformation(self, transform, matrix):
        transform.setMatrix(matrix * self._get_cylinder_transformatrion_matrix())

    def _redo_neutron_transformation(self, transform, matrix, offset):
        transform.setMatrix(matrix * self._get_sphere_transformation_matrix(offset))

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
