from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtCore import QPropertyAnimation
from PySide2.QtGui import QVector3D, QColor, QMatrix4x4
from ui.NeutronAnimationController import NeutronAnimationController


class InstrumentView(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        self.view = Qt3DExtras.Qt3DWindow()
        container = QWidget.createWindowContainer(self.view)
        lay.addWidget(container)

        self.view.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
        self.view.camera().setPosition(QVector3D(6, 8, 30))
        self.view.camera().setViewCenter(QVector3D(0, 0, 0))

        self.rootEntity = Qt3DCore.QEntity()
        cameraEntity = self.view.camera()
        camController = Qt3DExtras.QFirstPersonCameraController(self.rootEntity)
        camController.setLinearSpeed(20)
        camController.setCamera(cameraEntity)
        self.view.setRootEntity(self.rootEntity)

        self.initialise_view()

    def create_materials(self):

        red = QColor("red")
        black = QColor("black")
        grey = QColor("grey")
        blue = QColor("blue")
        lightblue = QColor("lightblue")
        darkred = QColor("#b00")

        self.grey_material = Qt3DExtras.QPhongMaterial()
        self.grey_material.setAmbient(black)
        self.grey_material.setDiffuse(grey)

        self.red_material = Qt3DExtras.QPhongMaterial()
        self.red_material.setAmbient(red)
        self.red_material.setDiffuse(darkred)

        self.beam_material = Qt3DExtras.QPhongAlphaMaterial()
        self.beam_material.setAmbient(blue)
        self.beam_material.setDiffuse(lightblue)
        self.beam_material.setAlpha(0.5)

        self.green_material = Qt3DExtras.QPhongMaterial()
        self.green_material.setAmbient(grey)
        self.green_material.setDiffuse(grey)

    def create_sample_cube(self):

        self.cubeEntity = Qt3DCore.QEntity(self.rootEntity)
        self.cubeMesh = Qt3DExtras.QCuboidMesh()
        self.cubeMesh.setXExtent(1)
        self.cubeMesh.setYExtent(1)
        self.cubeMesh.setZExtent(1)

        self.cubeEntity.addComponent(self.cubeMesh)
        self.cubeEntity.addComponent(self.red_material)

    def create_beam_cylinder(self):

        self.cylinderEntity = Qt3DCore.QEntity(self.rootEntity)
        self.cylinderMesh = Qt3DExtras.QCylinderMesh()
        self.cylinderMesh.setRadius(2.5)
        self.cylinderMesh.setLength(40)
        self.cylinderMesh.setRings(2)

        cylinderMatrix = QMatrix4x4()
        cylinderMatrix.rotate(270, QVector3D(1, 0, 0))
        cylinderMatrix.translate(QVector3D(0, 20, 0))

        self.cylinderTransform = Qt3DCore.QTransform()
        self.cylinderTransform.setMatrix(cylinderMatrix)

        self.cylinderEntity.addComponent(self.cylinderMesh)
        self.cylinderEntity.addComponent(self.beam_material)
        self.cylinderEntity.addComponent(self.cylinderTransform)

    def create_neutrons(self):

        self.neutronEntities = []
        self.neutronMeshes = []
        self.neutronTransforms = []
        self.neutronAnimationControllers = []
        self.neutronAnimations = []

        xOffsets = [0, 0, 0, 2, -2, 1.4, 1.4, -1.4, -1.4]
        yOffsets = [0, 2, -2, 0, 0, 1.4, -1.4, 1.4, -1.4]
        timeSpanOffsets = [0, -5, -7, 5, 7, 19, -19, 23, -23]

        for i in range(9):

            neutronEntity = Qt3DCore.QEntity(self.rootEntity)
            neutronMesh = Qt3DExtras.QSphereMesh()
            neutronMesh.setRadius(3)

            neutronTransform = Qt3DCore.QTransform()
            neutronAnimationController = NeutronAnimationController(
                xOffsets[i], yOffsets[i], neutronTransform
            )
            neutronAnimationController.setTarget(neutronTransform)

            neutronAnimation = QPropertyAnimation(neutronTransform)
            neutronAnimation.setTargetObject(neutronAnimationController)
            neutronAnimation.setPropertyName(b"distance")
            neutronAnimation.setStartValue(-40)
            neutronAnimation.setEndValue(0)
            neutronAnimation.setDuration(500 + timeSpanOffsets[i])
            neutronAnimation.setLoopCount(-1)
            neutronAnimation.start()

            self.neutronEntities.append(neutronEntity)
            self.neutronMeshes.append(neutronMesh)
            self.neutronTransforms.append(neutronTransform)
            self.neutronAnimationControllers.append(neutronAnimationController)
            self.neutronAnimations.append(neutronAnimation)

            neutronEntity.addComponent(neutronMesh)
            neutronEntity.addComponent(self.grey_material)
            neutronEntity.addComponent(neutronTransform)

    def initialise_view(self):

        self.create_materials()
        self.create_sample_cube()
        self.create_neutrons()
        self.create_beam_cylinder()
