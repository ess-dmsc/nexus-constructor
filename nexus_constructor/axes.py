from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtGui import QMatrix4x4, QVector3D, QColor


class Axes(object):
    def __init__(self, component_root_entity, far_plane, component_adder):

        self.component_root_entity = component_root_entity

        self.x_cylinder_entity = Qt3DCore.QEntity(self.component_root_entity)
        self.y_cylinder_entity = Qt3DCore.QEntity(self.component_root_entity)
        self.z_cylinder_entity = Qt3DCore.QEntity(self.component_root_entity)

        self.x_cylinder_mesh = Qt3DExtras.QCylinderMesh()
        self.y_cylinder_mesh = Qt3DExtras.QCylinderMesh()
        self.z_cylinder_mesh = Qt3DExtras.QCylinderMesh()

        self.x_cylinder_transformation = Qt3DCore.QTransform()
        self.y_cylinder_transformation = Qt3DCore.QTransform()
        self.z_cylinder_transformation = Qt3DCore.QTransform()

        self.add_qcomponents_to_entity = component_adder

        self.x_material = Qt3DExtras.QPhongMaterial()
        self.y_material = Qt3DExtras.QPhongMaterial()
        self.z_material = Qt3DExtras.QPhongMaterial()

        self.prepare_axes_material(self.x_material, "red")
        self.prepare_axes_material(self.y_material, "green")
        self.prepare_axes_material(self.z_material, "blue")

        self.cylinder_length = far_plane

    def setup_central_axes(self):

        self.configure_central_axes_cylinders(
            self.x_cylinder_mesh, self.cylinder_length
        )
        self.configure_central_axes_cylinders(
            self.y_cylinder_mesh, self.cylinder_length
        )
        self.configure_central_axes_cylinders(
            self.z_cylinder_mesh, self.cylinder_length
        )

        x_matrix, y_matrix, z_matrix = self.create_central_axes_matrices(
            self.cylinder_length
        )

        self.x_cylinder_transformation.setMatrix(x_matrix)
        self.y_cylinder_transformation.setMatrix(y_matrix)
        self.z_cylinder_transformation.setMatrix(z_matrix)

        self.add_qcomponents_to_entity(
            self.x_cylinder_entity,
            [self.x_cylinder_mesh, self.x_cylinder_transformation, self.x_material],
        )
        self.add_qcomponents_to_entity(
            self.y_cylinder_entity,
            [self.y_cylinder_mesh, self.y_cylinder_transformation, self.y_material],
        )
        self.add_qcomponents_to_entity(
            self.z_cylinder_entity,
            [self.z_cylinder_mesh, self.z_cylinder_transformation, self.z_material],
        )

    @staticmethod
    def configure_central_axes_cylinders(cylinder_mesh, cylinder_length):

        cylinder_mesh.setRadius(0.01)
        cylinder_mesh.setLength(cylinder_length)
        cylinder_mesh.setRings(2)

    @staticmethod
    def create_central_axes_matrices(length):
        """
        Construct the matrices that are used to transform the cylinders so that they form a gnomon. Note to self: this is a duplicate method!
        :param length: The length of the cylinders.
        :return: The transformation matrices.
        """
        x_axis_matrix = QMatrix4x4()
        y_axis_matrix = QMatrix4x4()
        z_axis_matrix = QMatrix4x4()

        # When the cylinders are born they are centered on the origin creating a "3D asterisk" shape. A translation of
        # half the length of the cylinders is required to make them form a gnomon.
        half_length = length * 0.5

        x_axis_matrix.rotate(270, QVector3D(0, 0, 1))
        x_axis_matrix.translate(QVector3D(0, half_length, 0))

        y_axis_matrix.translate(QVector3D(0, half_length, 0))

        z_axis_matrix.rotate(90, QVector3D(1, 0, 0))
        z_axis_matrix.translate(QVector3D(0, half_length, 0))

        return x_axis_matrix, y_axis_matrix, z_axis_matrix

    @staticmethod
    def prepare_axes_material(material, color):
        """
        Prepares the material that will be used to color the gnomon cylinders and sets its shininess to zero. Note to self: duplicated method.
        :param material: The material to be configured.
        :param color: The desired ambient color of the material.
        """
        material.setAmbient(color)
        material.setDiffuse(QColor("grey"))
        material.setShininess(0)
