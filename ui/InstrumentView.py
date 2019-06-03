from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtGui import QVector3D, QColor

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

        self.create_materials()
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

    def initialise_view(self):

        self.cubeEntity = Qt3DCore.QEntity(self.rootEntity)
        self.cubeMesh = Qt3DExtras.QCuboidMesh()
        self.cubeMesh.setXExtent(5)
        self.cubeMesh.setYExtent(5)
        self.cubeMesh.setZExtent(5)

        '''
        self.sphereTransform = Qt3DCore.QTransform()
        self.sphereTransform.setTranslation(QVector3D(x, y, z))
        '''

        self.cubeEntity.addComponent(self.cubeMesh)
        self.cubeEntity.addComponent(self.red_material)
        # self.cubeEntity.addComponent(self.sphereTransform)

        print("Created cube.")
