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

        self.rootEntity = Qt3DCore.QEntity()
        camera_entity = self.view.camera()
        cam_controller = Qt3DExtras.QFirstPersonCameraController(self.rootEntity)
        cam_controller.setLinearSpeed(20)
        cam_controller.setCamera(camera_entity)
        self.view.setRootEntity(self.rootEntity)

        # Initialise materials
        self.grey_material = Qt3DExtras.QPhongMaterial()
        self.red_material = Qt3DExtras.QPhongMaterial()
        self.beam_material = Qt3DExtras.QPhongAlphaMaterial()
        self.green_material = Qt3DExtras.QPhongMaterial()

        # Initialise cube objects
        self.cube_entity = Qt3DCore.QEntity(self.rootEntity)
        self.cube_mesh = Qt3DExtras.QCuboidMesh()

        # Create lists for neutron-related objects
        self.neutron_entities = []
        self.neutron_meshes = []
        self.neutron_transforms = []
        self.neutron_animation_controllers = []
        self.neutron_animations = []

        self.num_neutrons = 9
        self.cylinder_length = 40

        self.initialise_view()

        # Initialise beam objects
        self.cylinder_entity = Qt3DCore.QEntity(self.rootEntity)
        self.cylinder_mesh = Qt3DExtras.QCylinderMesh()
        self.cylinder_transform = Qt3DCore.QTransform()

        # Insert the beam cylinder last. This ensures that the semi-transparency works correctly.
        self.create_beam_cylinder(
            self.cylinder_mesh,
            self.cylinder_transform,
            self.cylinder_entity,
            self.cylinder_length,
            self.beam_material,
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

    def create_materials(self):
        """
        Creates the materials for the the objects that will inhabit the instrument view.
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
    def create_sample_cube(cube_mesh, cube_entity, material):
        """
        Create a 1x1x1 cube given a mesh, an entity, and a material.
        """
        cube_mesh.setXExtent(1)
        cube_mesh.setYExtent(1)
        cube_mesh.setZExtent(1)

        cube_entity.addComponent(cube_mesh)
        cube_entity.addComponent(material)

    @staticmethod
    def create_beam_cylinder(
        cylinder_mesh, cylinder_transform, cylinder_entity, cylinder_length, material
    ):
        """
        Creates the initial beam cylinder.
        """
        cylinder_mesh.setRadius(2.5)
        cylinder_mesh.setLength(cylinder_length)
        cylinder_mesh.setRings(2)

        cylinder_matrix = QMatrix4x4()
        cylinder_matrix.rotate(270, QVector3D(1, 0, 0))
        cylinder_matrix.translate(QVector3D(0, 20, 0))

        cylinder_transform.setMatrix(cylinder_matrix)

        cylinder_entity.addComponent(cylinder_mesh)
        cylinder_entity.addComponent(material)
        cylinder_entity.addComponent(cylinder_transform)

    def create_neutrons(self):
        """
        Creates the neutron animations.
        """
        # Create lists of x, y, and time offsets for the neutron animations
        x_offsets = [0, 0, 0, 2, -2, 1.4, 1.4, -1.4, -1.4]
        y_offsets = [0, 2, -2, 0, 0, 1.4, -1.4, 1.4, -1.4]
        time_span_offsets = [0, -5, -7, 5, 7, 19, -19, 23, -23]

        for i in range(self.num_neutrons):

            # Create the neutron mesh and entity
            neutron_entity = Qt3DCore.QEntity(self.rootEntity)
            neutron_mesh = Qt3DExtras.QSphereMesh()
            neutron_mesh.setRadius(3)

            neutron_transform = Qt3DCore.QTransform()
            neutron_animation_controller = NeutronAnimationController(
                x_offsets[i], y_offsets[i], neutron_transform
            )
            neutron_animation_controller.set_target(neutron_transform)

            # Instruct the NeutronAnimationController to move the neutron along the z-axis from -40 to 0
            neutron_animation = QPropertyAnimation(neutron_transform)
            neutron_animation.setTargetObject(neutron_animation_controller)
            neutron_animation.setPropertyName(b"distance")
            neutron_animation.setStartValue(-self.cylinder_length)
            neutron_animation.setEndValue(0)
            neutron_animation.setDuration(500 + time_span_offsets[i])
            neutron_animation.setLoopCount(-1)
            neutron_animation.start()

            self.neutron_entities.append(neutron_entity)
            self.neutron_meshes.append(neutron_mesh)
            self.neutron_transforms.append(neutron_transform)
            self.neutron_animation_controllers.append(neutron_animation_controller)
            self.neutron_animations.append(neutron_animation)

            neutron_entity.addComponent(neutron_mesh)
            neutron_entity.addComponent(self.grey_material)
            neutron_entity.addComponent(neutron_transform)

    def initialise_view(self):

        self.create_materials()
        self.create_sample_cube(self.cube_mesh, self.cube_entity, self.red_material)
        self.create_neutrons()
