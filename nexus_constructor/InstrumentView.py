from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtCore import QPropertyAnimation
from PySide2.QtGui import QVector3D, QColor, QMatrix4x4
from nexus_constructor.NeutronAnimationController import NeutronAnimationController


class InstrumentView(QWidget):
    """
    Class for managing the 3D view in the NeXus Constructor. Creates the initial sample, the initial beam, and the
    neutron animation.
    :param parent: The MainWindow in which this widget is created. This isn't used for anything but is accepted as an
                   argument in order to appease Qt Designer.
    """

    def __init__(self, parent):
        super().__init__()
        lay = QVBoxLayout(self)
        self.view = Qt3DExtras.Qt3DWindow()
        self.view.defaultFrameGraph().setClearColor(QColor("lightgrey"))
        container = QWidget.createWindowContainer(self.view)
        lay.addWidget(container)

        self.view.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
        self.view.camera().setPosition(QVector3D(6, 8, 30))
        self.view.camera().setViewCenter(QVector3D(0, 0, 0))

        self.root_entity = Qt3DCore.QEntity()
        camera_entity = self.view.camera()
        cam_controller = Qt3DExtras.QFirstPersonCameraController(self.root_entity)
        cam_controller.setLinearSpeed(20)
        cam_controller.setCamera(camera_entity)
        self.view.setRootEntity(self.root_entity)

        # Initialise materials
        self.grey_material = Qt3DExtras.QPhongMaterial()
        self.red_material = Qt3DExtras.QPhongMaterial()
        self.beam_material = Qt3DExtras.QPhongAlphaMaterial()
        self.green_material = Qt3DExtras.QPhongMaterial()

        # Initialise cube objects
        self.sample_cube_dimensions = [1, 1, 1]
        self.cube_entity = Qt3DCore.QEntity(self.root_entity)
        self.cube_mesh = Qt3DExtras.QCuboidMesh()

        self.num_neutrons = 9

        # Create lists for neutron-related objects
        self.neutron_entities = [
            Qt3DCore.QEntity(self.root_entity) for _ in range(self.num_neutrons)
        ]
        self.neutron_meshes = [
            Qt3DExtras.QSphereMesh() for _ in range(self.num_neutrons)
        ]
        self.neutron_transforms = [
            Qt3DCore.QTransform() for _ in range(self.num_neutrons)
        ]
        self.neutron_animation_controllers = []
        self.neutron_animations = []

        self.cylinder_length = 40

        self.initialise_view()

        # Initialise beam objects
        self.cylinder_entity = Qt3DCore.QEntity(self.root_entity)
        self.cylinder_mesh = Qt3DExtras.QCylinderMesh()
        self.cylinder_transform = Qt3DCore.QTransform()

        # Insert the beam cylinder last. This ensures that the semi-transparency works correctly.
        self.set_cylinder_mesh_properties(
            self.cylinder_mesh, 2.5, self.cylinder_length, 2
        )
        self.set_beam_transform(self.cylinder_transform)
        self.add_components_to_entity(
            self.cylinder_entity,
            [self.cylinder_mesh, self.beam_material, self.cylinder_transform],
        )

    @staticmethod
    def set_material_properties(material, ambient, diffuse, alpha=None):
        """
        Set the ambient, diffuse, and alpha properties of a material.
        :param material: The material to be modified.
        :param ambient: The desired ambient colour of the material.
        :param diffuse: The desired diffuse colour of the material.
        :param alpha: The desired alpha value of the material. Optional argument as not all material-types have this
                         property.
        """
        material.setAmbient(ambient)
        material.setDiffuse(diffuse)

        if alpha is not None:
            material.setAlpha(alpha)

    def give_colours_to_materials(self):
        """
        Creates several QColours and uses them to configure the different materials that will be used for the objects in
        the 3D view.
        """
        red = QColor("red")
        black = QColor("black")
        grey = QColor("grey")
        blue = QColor("blue")
        light_blue = QColor("lightblue")
        dark_red = QColor("#b00")

        self.set_material_properties(self.grey_material, black, grey)
        self.set_material_properties(self.red_material, red, dark_red)
        self.set_material_properties(self.green_material, grey, grey)
        self.set_material_properties(self.beam_material, blue, light_blue, 0.5)

    @staticmethod
    def set_cube_mesh_dimensions(cube_mesh, x, y, z):

        cube_mesh.setXExtent(x)
        cube_mesh.setYExtent(y)
        cube_mesh.setZExtent(z)

    @staticmethod
    def add_components_to_entity(entity, components):
        """
        Takes a QEntity and gives it all of the components that are contained in a list.
        """
        for component in components:
            entity.addComponent(component)

    @staticmethod
    def set_cylinder_mesh_properties(cylinder_mesh, radius, length, rings):

        cylinder_mesh.setRadius(radius)
        cylinder_mesh.setLength(length)
        cylinder_mesh.setRings(rings)

    @staticmethod
    def set_beam_transform(cylinder_transform):
        """
        Creates the initial beam cylinder.
        """
        cylinder_matrix = QMatrix4x4()
        cylinder_matrix.rotate(270, QVector3D(1, 0, 0))
        cylinder_matrix.translate(QVector3D(0, 20, 0))

        cylinder_transform.setMatrix(cylinder_matrix)

    @staticmethod
    def set_sphere_mesh_radius(sphere_mesh):

        # Create a neutron mesh with a fixed radius
        sphere_mesh.setRadius(3)

    @staticmethod
    def create_neutron_animation(
        x_offset, y_offset, neutron_transform, animation_distance, time_span_offset
    ):

        neutron_animation_controller = NeutronAnimationController(
            x_offset, y_offset, neutron_transform
        )
        neutron_animation_controller.set_target(neutron_transform)

        # Instruct the NeutronAnimationController to move the neutron along the z-axis from -40 to 0
        neutron_animation = QPropertyAnimation(neutron_transform)
        neutron_animation.setTargetObject(neutron_animation_controller)
        neutron_animation.setPropertyName(b"distance")
        neutron_animation.setStartValue(animation_distance)
        neutron_animation.setEndValue(0)
        neutron_animation.setDuration(500 + time_span_offset)
        neutron_animation.setLoopCount(-1)
        neutron_animation.start()

        return neutron_animation, neutron_animation_controller

    def create_neutrons(self):
        """
        Creates the neutron animations.
        """
        # Create lists of x, y, and time offsets for the neutron animations
        x_offsets = [0, 0, 0, 2, -2, 1.4, 1.4, -1.4, -1.4]
        y_offsets = [0, 2, -2, 0, 0, 1.4, -1.4, 1.4, -1.4]
        time_span_offsets = [0, -5, -7, 5, 7, 19, -19, 23, -23]

        for i in range(self.num_neutrons):

            neutron_animation, neutron_animation_controller = self.create_neutron_animation(
                x_offsets[i],
                y_offsets[i],
                self.neutron_transforms[i],
                -self.cylinder_length,
                time_span_offsets[i],
            )

            self.neutron_animation_controllers.append(neutron_animation_controller)
            self.neutron_animations.append(neutron_animation)

            self.add_components_to_entity(
                self.neutron_entities[i],
                [
                    self.neutron_meshes[i],
                    self.grey_material,
                    self.neutron_transforms[i],
                ],
            )

    def initialise_view(self):

        self.give_colours_to_materials()

        self.set_cube_mesh_dimensions(self.cube_mesh, *self.sample_cube_dimensions)
        self.add_components_to_entity(
            self.cube_entity, [self.cube_mesh, self.red_material]
        )
        self.create_neutrons()
