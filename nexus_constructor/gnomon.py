from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtGui import QVector3D, QMatrix4x4, QColor, QFont, QVector4D


class Gnomon:
    def __init__(self, root_entity, main_camera, component_adder):

        self.gnomon_root_entity = root_entity
        self.gnomon_cylinder_length = 4
        self.main_camera = main_camera
        self.gnomon_camera = self.create_gnomon_camera(main_camera)

        self.x_axis_entity = Qt3DCore.QEntity(self.gnomon_root_entity)
        self.y_axis_entity = Qt3DCore.QEntity(self.gnomon_root_entity)
        self.z_axis_entity = Qt3DCore.QEntity(self.gnomon_root_entity)

        self.x_axis_mesh = Qt3DExtras.QCylinderMesh()
        self.y_axis_mesh = Qt3DExtras.QCylinderMesh()
        self.z_axis_mesh = Qt3DExtras.QCylinderMesh()

        self.x_axis_transformation = Qt3DCore.QTransform()
        self.y_axis_transformation = Qt3DCore.QTransform()
        self.z_axis_transformation = Qt3DCore.QTransform()

        self.x_cone_entity = Qt3DCore.QEntity(self.gnomon_root_entity)
        self.y_cone_entity = Qt3DCore.QEntity(self.gnomon_root_entity)
        self.z_cone_entity = Qt3DCore.QEntity(self.gnomon_root_entity)

        self.x_cone_mesh = Qt3DExtras.QConeMesh(self.gnomon_root_entity)
        self.y_cone_mesh = Qt3DExtras.QConeMesh(self.gnomon_root_entity)
        self.z_cone_mesh = Qt3DExtras.QConeMesh(self.gnomon_root_entity)

        self.x_cone_transformation = Qt3DCore.QTransform()
        self.y_cone_transformation = Qt3DCore.QTransform()
        self.z_cone_transformation = Qt3DCore.QTransform()

        self.x_axis_text = Qt3DExtras.QText2DEntity(self.gnomon_root_entity)
        self.y_axis_text = Qt3DExtras.QText2DEntity(self.gnomon_root_entity)
        self.z_axis_text = Qt3DExtras.QText2DEntity(self.gnomon_root_entity)

        self.x_text_transformation = Qt3DCore.QTransform()
        self.y_text_transformation = Qt3DCore.QTransform()
        self.z_text_transformation = Qt3DCore.QTransform()

        text_translation = self.gnomon_cylinder_length * 1.3

        self.x_text_vector = QVector3D(text_translation, -0.5, 0)
        self.y_text_vector = QVector3D(-0.4, text_translation, 0)
        self.z_text_vector = QVector3D(-0.5, -0.5, text_translation)

        # Borrowing a method from the instrument view?
        self.add_qcomponents_to_entity = component_adder

        self.x_material = Qt3DExtras.QPhongMaterial()
        self.y_material = Qt3DExtras.QPhongMaterial()
        self.z_material = Qt3DExtras.QPhongMaterial()

        self.prepare_gnomon_material(self.x_material, "red")
        self.prepare_gnomon_material(self.y_material, "green")
        self.prepare_gnomon_material(self.z_material, "blue")

    def get_gnomon_camera(self):
        return self.gnomon_camera

    @staticmethod
    def prepare_gnomon_material(material, color):

        material.setAmbient(color)
        material.setDiffuse(QColor("grey"))
        material.setShininess(0)

    @staticmethod
    def configure_gnomon_cylinder(cylinder_mesh, length):
        """
        Set the radius, length and ring properties of the cylinders that create the gnomon. The radius is 1/20th of the
        length and the number of rings is set to the smallest value that still creates the expected shape.
        :param cylinder_mesh: The mesh to be configured.
        :param length: The desired length of the cylinder.
        """
        cylinder_mesh.setRadius(length * 0.05)
        cylinder_mesh.setLength(length)
        cylinder_mesh.setRings(2)

    @staticmethod
    def create_cylinder_matrices(length):
        """
        Construct the matrices that are used to transform the cylinders so that they form a gnomon.
        :param length: The length of the cylinders.
        :return: The transformation matrices.
        """
        x_axis_matrix = QMatrix4x4()
        y_axis_matrix = QMatrix4x4()
        z_axis_matrix = QMatrix4x4()

        half_length = length * 0.5

        x_axis_matrix.rotate(270, QVector3D(0, 0, 1))
        x_axis_matrix.translate(QVector3D(0, half_length, 0))

        y_axis_matrix.translate(QVector3D(0, half_length, 0))

        z_axis_matrix.rotate(90, QVector3D(1, 0, 0))
        z_axis_matrix.translate(QVector3D(0, half_length, 0))

        return x_axis_matrix, y_axis_matrix, z_axis_matrix

    @staticmethod
    def create_cone_matrices(length):
        """
        Creates the matrices used to transform the cones that form the gnomon.
        :param length: The length of the gnomon cylinders.
        :return: The transformation matrices.
        """
        x_axis_matrix = QMatrix4x4()
        y_axis_matrix = QMatrix4x4()
        z_axis_matrix = QMatrix4x4()

        x_axis_matrix.rotate(270, QVector3D(0, 0, 1))
        x_axis_matrix.translate(QVector3D(0, length, 0))

        y_axis_matrix.translate(QVector3D(0, length, 0))

        z_axis_matrix.rotate(90, QVector3D(1, 0, 0))
        z_axis_matrix.translate(QVector3D(0, length, 0))

        return x_axis_matrix, y_axis_matrix, z_axis_matrix

    @staticmethod
    def create_axis_label_matrices(vectors):
        """
        Creates the matrices used to transform the labels that form the gnomon.
        :param vectors: The vectors that describe the location of the text.
        :return: The transformation matrices.
        """
        x_axis_matrix = QMatrix4x4()
        y_axis_matrix = QMatrix4x4()
        z_axis_matrix = QMatrix4x4()

        x_axis_matrix.translate(vectors[0])
        y_axis_matrix.translate(vectors[1])
        z_axis_matrix.translate(vectors[2])

        return x_axis_matrix, y_axis_matrix, z_axis_matrix

    @staticmethod
    def configure_gnomon_cone(cone_mesh, gnomon_cylinder_length):

        cone_mesh.setLength(gnomon_cylinder_length * 0.3)
        cone_mesh.setBottomRadius(gnomon_cylinder_length * 0.1)
        cone_mesh.setTopRadius(0)

    def create_gnomon(self):

        self.create_gnomon_cylinders()
        self.create_gnomon_cones()
        self.create_gnomon_text()

    def create_gnomon_text(self):
        self.set_axis_label_text(self.x_axis_text, "X", "red")
        self.set_axis_label_text(self.y_axis_text, "Y", "green")
        self.set_axis_label_text(self.z_axis_text, "Z", "blue")
        x_label_matrix, y_label_matrix, z_label_matrix = self.create_axis_label_matrices(
            [self.x_text_vector, self.y_text_vector, self.z_text_vector]
        )

        self.x_text_transformation.setMatrix(x_label_matrix)
        self.y_text_transformation.setMatrix(y_label_matrix)
        self.z_text_transformation.setMatrix(z_label_matrix)

        self.x_axis_text.addComponent(self.x_text_transformation)
        self.y_axis_text.addComponent(self.y_text_transformation)
        self.z_axis_text.addComponent(self.z_text_transformation)

    def create_gnomon_cones(self):
        self.configure_gnomon_cone(self.x_cone_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cone(self.y_cone_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cone(self.z_cone_mesh, self.gnomon_cylinder_length)
        x_cone_matrix, y_cone_matrix, z_cone_matrix = self.create_cone_matrices(
            self.gnomon_cylinder_length
        )
        self.x_cone_transformation.setMatrix(x_cone_matrix)
        self.y_cone_transformation.setMatrix(y_cone_matrix)
        self.z_cone_transformation.setMatrix(z_cone_matrix)
        self.add_qcomponents_to_entity(
            self.x_cone_entity,
            [self.x_cone_mesh, self.x_cone_transformation, self.x_material],
        )
        self.add_qcomponents_to_entity(
            self.y_cone_entity,
            [self.y_cone_mesh, self.y_cone_transformation, self.y_material],
        )
        self.add_qcomponents_to_entity(
            self.z_cone_entity,
            [self.z_cone_mesh, self.z_cone_transformation, self.z_material],
        )

    def create_gnomon_cylinders(self):

        self.configure_gnomon_cylinder(self.x_axis_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cylinder(self.y_axis_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cylinder(self.z_axis_mesh, self.gnomon_cylinder_length)
        x_axis_matrix, y_axis_matrix, z_axis_matrix = self.create_cylinder_matrices(
            self.gnomon_cylinder_length
        )
        self.x_axis_transformation.setMatrix(x_axis_matrix)
        self.y_axis_transformation.setMatrix(y_axis_matrix)
        self.z_axis_transformation.setMatrix(z_axis_matrix)
        self.add_qcomponents_to_entity(
            self.x_axis_entity,
            [self.x_axis_mesh, self.x_axis_transformation, self.x_material],
        )
        self.add_qcomponents_to_entity(
            self.y_axis_entity,
            [self.y_axis_mesh, self.y_axis_transformation, self.y_material],
        )
        self.add_qcomponents_to_entity(
            self.z_axis_entity,
            [self.z_axis_mesh, self.z_axis_transformation, self.z_material],
        )

    @staticmethod
    def set_axis_label_text(text_entity, text_label, color):

        text_entity.setText(text_label)
        text_entity.setHeight(1.2)
        text_entity.setWidth(1)
        text_entity.setColor(QColor(color))
        text_entity.setFont(QFont("Courier New", 1))

    def create_gnomon_camera(self, main_camera):
        gnomon_camera = Qt3DRender.QCamera()
        gnomon_camera.setParent(self.gnomon_root_entity)
        gnomon_camera.setProjectionType(main_camera.projectionType())
        gnomon_camera.lens().setPerspectiveProjection(
            main_camera.fieldOfView(), 1, 0.1, 25
        )
        gnomon_camera.setUpVector(main_camera.upVector())
        gnomon_camera.setViewCenter(QVector3D(0, 0, 0))
        return gnomon_camera

    def update_gnomon(self):

        self.update_gnomon_camera()
        self.update_gnomon_text()

    def update_gnomon_camera(self):

        updated_gnomon_camera_position = (
            self.main_camera.position() - self.main_camera.viewCenter()
        )
        updated_gnomon_camera_position = updated_gnomon_camera_position.normalized()
        updated_gnomon_camera_position *= self.gnomon_cylinder_length * 4

        self.gnomon_camera.setPosition(updated_gnomon_camera_position)
        self.gnomon_camera.setUpVector(self.main_camera.upVector())

    def update_gnomon_text(self):
        view_matrix = self.gnomon_camera.viewMatrix()
        self.x_text_transformation.setMatrix(
            self.create_billboard_transformation(view_matrix, self.x_text_vector)
        )
        self.y_text_transformation.setMatrix(
            self.create_billboard_transformation(view_matrix, self.y_text_vector)
        )
        self.z_text_transformation.setMatrix(
            self.create_billboard_transformation(view_matrix, self.z_text_vector)
        )

    @staticmethod
    def create_billboard_transformation(view_matrix, text_vector):

        view_transpose = view_matrix.transposed()
        view_transpose.setRow(3, QVector4D())
        view_transpose.setColumn(3, QVector4D(text_vector, 1))
        return view_transpose
