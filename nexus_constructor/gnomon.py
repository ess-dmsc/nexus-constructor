from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtCore import QPropertyAnimation
from PySide2.QtGui import QVector3D, QMatrix4x4, QColor, QFont, QVector4D

from nexus_constructor.axis_colors import AxisColors
from nexus_constructor.neutron_animation_controller import NeutronAnimationController
from nexus_constructor.qentity_utils import create_material, add_qcomponents_to_entity


class Gnomon:
    def __init__(self, root_entity, main_camera, beam_material, grey_material):
        """
        A class that houses the Qt3D items (entities, transformations, etc) related to the gnomon (or axis indicator).
        The gnomon/axis indicator is an object that appears in the bottom right-hand corner of the instrument view that
        shows the direction of the x, y, and z axes.
        :param root_entity: The root entity for the gnomon.
        :param beam_material: The semi-transparent material that is used for the beam in the gnomon.
        :param grey_material: The material that is used to pain the neutrons.
        :param main_camera: The main component view camera.
        """

        self.gnomon_root_entity = root_entity
        self.gnomon_cylinder_length = 4
        self.main_camera = main_camera
        self.gnomon_camera = self.create_gnomon_camera(main_camera)
        self.beam_material = beam_material
        self.grey_material = grey_material

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

        # Set the text translation value to be the length of the cylinder plus some extra space so that it doesn't
        # overlap with the cylinder or the cones.
        text_translation = self.gnomon_cylinder_length * 1.3

        # The text translation value calculated above is used in addition to some "extra" values in order to make the
        # text placement look good and appear centered next to the cone point. This extra values were found via trial
        # and error and will likely have to be figured out again if you decide to change the font/size/height/etc of
        # the text.
        self.x_text_vector = QVector3D(text_translation, -0.5, 0)
        self.y_text_vector = QVector3D(-0.4, text_translation, 0)
        self.z_text_vector = QVector3D(-0.5, -0.5, text_translation)

        self.x_material = Qt3DExtras.QPhongMaterial()
        self.y_material = Qt3DExtras.QPhongMaterial()
        self.z_material = Qt3DExtras.QPhongMaterial()

        diffuse_color = QColor("grey")

        self.x_material = create_material(
            AxisColors.X.value, diffuse_color, remove_shininess=True
        )
        self.y_material = create_material(
            AxisColors.Y.value, diffuse_color, remove_shininess=True
        )
        self.z_material = create_material(
            AxisColors.Z.value, diffuse_color, remove_shininess=True
        )

        # Initialise beam objects
        self.cylinder_entity = Qt3DCore.QEntity(self.gnomon_root_entity)
        self.cylinder_mesh = Qt3DExtras.QCylinderMesh()
        self.cylinder_transform = Qt3DCore.QTransform()

        self.num_neutrons = 9

        self.neutron_animation_length = self.gnomon_cylinder_length * 1.5

        # Create a dictionary for neutron-related objects so that they are always in scope and not destroyed by C++
        self.neutron_objects = {
            "entities": [],
            "meshes": [],
            "transforms": [],
            "animation_controllers": [],
            "animations": [],
        }

        for _ in range(self.num_neutrons):
            self.neutron_objects["entities"].append(
                Qt3DCore.QEntity(self.gnomon_root_entity)
            )
            self.neutron_objects["meshes"].append(Qt3DExtras.QSphereMesh())
            self.neutron_objects["transforms"].append(Qt3DCore.QTransform())

    def get_gnomon_camera(self):
        """
        :return: The camera that observes the gnomon.
        """
        return self.gnomon_camera

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
        """
        Gives a shape to the gnomon cone mesh by setting its length and top/bottom radii. The cone length is set to
        3/10ths of the cylinder length, the cone bottom radius is 1/10th of the cylinder length (or double the cylinder
        radius), and the top radius is set to zero in order to make a point.
        :param cone_mesh: The mesh to be configured.
        :param gnomon_cylinder_length: The length of the gnomon cylinders. Used to determine the shape of the cones.
        """
        cone_mesh.setLength(gnomon_cylinder_length * 0.3)
        cone_mesh.setBottomRadius(gnomon_cylinder_length * 0.1)
        cone_mesh.setTopRadius(0)

    def create_gnomon(self):
        """
        Sets up the gnomon by creating the cylinders, cones, and text.
        """
        self.create_gnomon_cylinders()
        self.create_gnomon_cones()
        self.create_gnomon_text()

    def create_gnomon_text(self):
        """
        Prepares the gnomon text by creating text entities and then placing them at the ends of the cones.
        """
        self.set_axis_label_text(self.x_axis_text, "X", AxisColors.X.value)
        # Pass "green" rather than the Y axis enum value because otherwise the text is too bright
        self.set_axis_label_text(self.y_axis_text, "Y", QColor("green"))
        self.set_axis_label_text(self.z_axis_text, "Z", AxisColors.Z.value)
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
        """
        Prepares the gnomon cones by configuring the meshes and then placing them at the ends of the cylinders.
        """
        self.configure_gnomon_cone(self.x_cone_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cone(self.y_cone_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cone(self.z_cone_mesh, self.gnomon_cylinder_length)
        x_cone_matrix, y_cone_matrix, z_cone_matrix = self.create_cone_matrices(
            self.gnomon_cylinder_length
        )
        self.x_cone_transformation.setMatrix(x_cone_matrix)
        self.y_cone_transformation.setMatrix(y_cone_matrix)
        self.z_cone_transformation.setMatrix(z_cone_matrix)
        add_qcomponents_to_entity(
            self.x_cone_entity,
            [self.x_cone_mesh, self.x_cone_transformation, self.x_material],
        )
        add_qcomponents_to_entity(
            self.y_cone_entity,
            [self.y_cone_mesh, self.y_cone_transformation, self.y_material],
        )
        add_qcomponents_to_entity(
            self.z_cone_entity,
            [self.z_cone_mesh, self.z_cone_transformation, self.z_material],
        )

    def create_gnomon_cylinders(self):
        """
        Configures three cylinder meshes and translates them in order to create a basic gnomon shape.
        """
        self.configure_gnomon_cylinder(self.x_axis_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cylinder(self.y_axis_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cylinder(self.z_axis_mesh, self.gnomon_cylinder_length)
        x_axis_matrix, y_axis_matrix, z_axis_matrix = self.create_cylinder_matrices(
            self.gnomon_cylinder_length
        )
        self.x_axis_transformation.setMatrix(x_axis_matrix)
        self.y_axis_transformation.setMatrix(y_axis_matrix)
        self.z_axis_transformation.setMatrix(z_axis_matrix)
        add_qcomponents_to_entity(
            self.x_axis_entity,
            [self.x_axis_mesh, self.x_axis_transformation, self.x_material],
        )
        add_qcomponents_to_entity(
            self.y_axis_entity,
            [self.y_axis_mesh, self.y_axis_transformation, self.y_material],
        )
        add_qcomponents_to_entity(
            self.z_axis_entity,
            [self.z_axis_mesh, self.z_axis_transformation, self.z_material],
        )

    @staticmethod
    def set_axis_label_text(text_entity, text_label, text_color):
        """
        Configures the text used for the axis labels.
        :param text_entity: The text entity that will be used for the label.
        :param text_label: The text that the label needs to contain.
        :param text_color: The desired color of the label.
        """
        text_entity.setText(text_label)
        text_entity.setHeight(1.2)
        text_entity.setWidth(1)
        text_entity.setColor(QColor(text_color))
        text_entity.setFont(QFont("Courier New", 1))

    def create_gnomon_camera(self, main_camera):
        """
        Creates a camera for observing the gnomon. Borrows some settings from the main camera.
        :param main_camera: The main camera that views the instrument components.
        :return: The gnomon camera.
        """
        aspect = 1
        near_plane = 0.1

        # Set far plane so that the camera can see the gnomon even when it is turned "behind" it and the cylinders are
        # facing away from the camera.
        far_plane = 25

        gnomon_camera = Qt3DRender.QCamera()
        gnomon_camera.setParent(self.gnomon_root_entity)
        gnomon_camera.setProjectionType(main_camera.projectionType())
        gnomon_camera.lens().setPerspectiveProjection(
            main_camera.fieldOfView(), aspect, near_plane, far_plane
        )
        gnomon_camera.setUpVector(main_camera.upVector())
        gnomon_camera.setViewCenter(QVector3D(0, 0, 0))
        return gnomon_camera

    def update_gnomon(self):
        """
        Updates the gnomon when the main camera has moved by rotating the camera and transforming the axis labels.
        """
        self.update_gnomon_camera()
        self.update_gnomon_text()

    def update_gnomon_camera(self):
        """
        Rotates the gnomon camera so that it is consistent with the main camera.
        """
        updated_gnomon_camera_position = (
            self.main_camera.position() - self.main_camera.viewCenter()
        )
        updated_gnomon_camera_position = updated_gnomon_camera_position.normalized()
        updated_gnomon_camera_position *= self.gnomon_cylinder_length * 4.2

        self.gnomon_camera.setPosition(updated_gnomon_camera_position)
        self.gnomon_camera.setUpVector(self.main_camera.upVector())

    def update_gnomon_text(self):
        """
        Applies a billboard transformation to the axis label text so that it faces the gnomon camera.
        """
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
        """
        Uses the view matrix of the gnomon camera and the current position of the axis label text in order to create a
        matrix that makes the text plane orthogonal to the camera vector.
        :param view_matrix: The view matrix of the gnomon camera. This is the inverse of the translation matrix that
                            describes the position and rotation of the camera.
        :param text_vector: The vector of the axis label text.
        :return: A transformation matrix for making the text face the camera.
        """
        billboard_transformation = view_matrix.transposed()
        billboard_transformation.setRow(3, QVector4D())
        billboard_transformation.setColumn(3, QVector4D(text_vector, 1))
        return billboard_transformation

    @staticmethod
    def set_cylinder_mesh_dimensions(cylinder_mesh, radius, length, rings):
        """
        Sets the dimensions of a cylinder mesh.
        :param cylinder_mesh: The cylinder mesh to modify.
        :param radius: The desired radius.
        :param length: The desired length.
        :param rings: The desired number of rings.
        """
        cylinder_mesh.setRadius(radius)
        cylinder_mesh.setLength(length)
        cylinder_mesh.setRings(rings)

    @staticmethod
    def set_beam_transform(cylinder_transform, neutron_animation_distance):
        """
        Configures the transform for the beam cylinder by giving it a matrix. The matrix will turn the cylinder sideways
        and then move it "backwards" in the z-direction by 20 units so that it ends at the location of the sample.
        :param cylinder_transform: A QTransform object.
        :param neutron_animation_distance: The distance that the neutron travels during its animation.
        """
        cylinder_matrix = QMatrix4x4()
        cylinder_matrix.rotate(90, QVector3D(1, 0, 0))
        cylinder_matrix.translate(QVector3D(0, neutron_animation_distance * 0.5, 0))

        cylinder_transform.setMatrix(cylinder_matrix)

    def setup_beam_cylinder(self):
        """
        Sets up the beam cylinder by giving the cylinder entity a mesh, a material, and a transformation.
        """
        self.set_cylinder_mesh_dimensions(
            self.cylinder_mesh, 1.5, self.neutron_animation_length, 2
        )
        self.set_beam_transform(self.cylinder_transform, self.neutron_animation_length)
        add_qcomponents_to_entity(
            self.cylinder_entity,
            [self.cylinder_mesh, self.beam_material, self.cylinder_transform],
        )

    @staticmethod
    def set_neutron_animation_properties(
        neutron_animation,
        neutron_animation_controller,
        animation_distance,
        time_span_offset,
    ):
        """
        Prepares a QPropertyAnimation for a neutron by giving it a target, a distance, and loop settings.
        :param neutron_animation: The QPropertyAnimation to be configured.
        :param neutron_animation_controller: The related animation controller object.
        :param animation_distance: The starting distance of the neutron.
        :param time_span_offset: The offset that allows the neutron to move at a different time from other neutrons.
        """
        neutron_animation.setTargetObject(neutron_animation_controller)
        neutron_animation.setPropertyName(b"distance")
        neutron_animation.setStartValue(0)
        neutron_animation.setEndValue(animation_distance)
        neutron_animation.setDuration(500 + time_span_offset)
        neutron_animation.setLoopCount(-1)
        neutron_animation.start()

    @staticmethod
    def set_sphere_mesh_radius(sphere_mesh, radius):
        """
        Sets the radius of a sphere mesh.
        :param sphere_mesh: The sphere mesh to modify.
        :param radius: The desired radius.
        """
        sphere_mesh.setRadius(radius)

    def setup_neutrons(self):
        """
        Sets up the neutrons and their animations by preparing their meshes and then giving offset and
        distance parameters to an animation controller.
        """

        # Create lists of x, y, and time offsets for the neutron animations
        x_offsets = [0, 0, 0, 2, -2, 1.4, 1.4, -1.4, -1.4]
        y_offsets = [0, 2, -2, 0, 0, 1.4, -1.4, 1.4, -1.4]
        time_span_offsets = [0, -5, -7, 5, 7, 19, -19, 23, -23]

        neutron_radius = 1.5

        for i in range(self.num_neutrons):

            self.set_sphere_mesh_radius(
                self.neutron_objects["meshes"][i], neutron_radius
            )

            neutron_animation_controller = NeutronAnimationController(
                x_offsets[i] * 0.5,
                y_offsets[i] * 0.5,
                self.neutron_objects["transforms"][i],
            )
            neutron_animation_controller.set_target(
                self.neutron_objects["transforms"][i]
            )

            neutron_animation = QPropertyAnimation(
                self.neutron_objects["transforms"][i]
            )
            self.set_neutron_animation_properties(
                neutron_animation,
                neutron_animation_controller,
                self.neutron_animation_length,
                time_span_offsets[i],
            )

            self.neutron_objects["animation_controllers"].append(
                neutron_animation_controller
            )
            self.neutron_objects["animations"].append(neutron_animation)

            add_qcomponents_to_entity(
                self.neutron_objects["entities"][i],
                [
                    self.neutron_objects["meshes"][i],
                    self.grey_material,
                    self.neutron_objects["transforms"][i],
                ],
            )
