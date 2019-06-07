from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtCore import QPropertyAnimation
from PySide2.QtGui import QVector3D, QColor, QMatrix4x4
from nexus_constructor.NeutronAnimationController import NeutronAnimationController


class InstrumentView(QWidget):
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

        for i in range(self.num_neutrons):
            self.neutron_entities.append(Qt3DCore.QEntity())
            self.neutron_meshes.append()

        # Initialise beam objects
        self.cylinder_entity = Qt3DCore.QEntity(self.rootEntity)
        self.cylinder_mesh = Qt3DExtras.QCylinderMesh()
        self.cylinder_length = 40

        self.initialise_view()

    def create_materials(self):
        """
        Creates the materials for the the objects that will inhabit the instrument view.
        """
        red = QColor("red")
        black = QColor("black")
        grey = QColor("grey")
        blue = QColor("blue")
        lightblue = QColor("lightblue")
        darkred = QColor("#b00")

        self.grey_material.setAmbient(black)
        self.grey_material.setDiffuse(grey)

        self.red_material.setAmbient(red)
        self.red_material.setDiffuse(darkred)

        self.beam_material.setAmbient(blue)
        self.beam_material.setDiffuse(lightblue)
        self.beam_material.setAlpha(0.5)

        self.green_material.setAmbient(grey)
        self.green_material.setDiffuse(grey)

    def create_sample_cube(self):
        """
        Creates the initial sample cube.
        """
        self.cube_mesh.setXExtent(1)
        self.cube_mesh.setYExtent(1)
        self.cube_mesh.setZExtent(1)

        self.cube_entity.addComponent(self.cube_mesh)
        self.cube_entity.addComponent(self.red_material)

    def create_beam_cylinder(self):
        """
        Creates the initial beam cylinder.
        """
        self.cylinder_mesh.setRadius(2.5)
        self.cylinder_mesh.setLength(self.cylinder_length)
        self.cylinder_mesh.setRings(2)

        cylinder_matrix = QMatrix4x4()
        cylinder_matrix.rotate(270, QVector3D(1, 0, 0))
        cylinder_matrix.translate(QVector3D(0, 20, 0))

        self.cylinderTransform = Qt3DCore.QTransform()
        self.cylinderTransform.setMatrix(cylinder_matrix)

        self.cylinder_entity.addComponent(self.cylinder_mesh)
        self.cylinder_entity.addComponent(self.beam_material)
        self.cylinder_entity.addComponent(self.cylinderTransform)

    def create_neutrons(self):
        """
        Creates the neutron animations.
        """
        # Create lists of x, y, and time offsets for the neutron animations
        x_offsets = [0, 0, 0, 2, -2, 1.4, 1.4, -1.4, -1.4]
        y_offsets = [0, 2, -2, 0, 0, 1.4, -1.4, 1.4, -1.4]
        time_span_offsets = [0, -5, -7, 5, 7, 19, -19, 23, -23]

        for i in range(9):

            # Create the neutron mesh and entity

            neutronMesh.setRadius(3)

            neutronTransform = Qt3DCore.QTransform()
            neutronAnimationController = NeutronAnimationController(
                x_offsets[i], y_offsets[i], neutronTransform
            )
            neutronAnimationController.setTarget(neutronTransform)

            # Instruct the NeutronAnimationController to move the neutron along the z-axis from -40 to 0
            neutronAnimation = QPropertyAnimation(neutronTransform)
            neutronAnimation.setTargetObject(neutronAnimationController)
            neutronAnimation.setPropertyName(b"distance")
            neutronAnimation.setStartValue(-self.cylinder_length)
            neutronAnimation.setEndValue(0)
            neutronAnimation.setDuration(500 + time_span_offsets[i])
            neutronAnimation.setLoopCount(-1)
            neutronAnimation.start()

            self.neutron_entities.append(neutronEntity)
            self.neutron_meshes.append(neutronMesh)
            self.neutron_transforms.append(neutronTransform)
            self.neutron_animation_controllers.append(neutronAnimationController)
            self.neutron_animations.append(neutronAnimation)

            neutronEntity.addComponent(neutronMesh)
            neutronEntity.addComponent(self.grey_material)
            neutronEntity.addComponent(neutronTransform)

    def initialise_view(self):

        self.create_materials()
        self.create_sample_cube()
        self.create_neutrons()
        self.create_beam_cylinder()
