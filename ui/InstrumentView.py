from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtGui import QVector3D

class InstrumentView(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        self.view = Qt3DExtras.Qt3DWindow()
        container = QWidget.createWindowContainer(self.view)
        lay.addWidget(container)

        self.view.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
        self.view.camera().setPosition(QVector3D(0, 0, 40))
        self.view.camera().setViewCenter(QVector3D(0, 0, 0))

        self.rootEntity = Qt3DCore.QEntity()
        cameraEntity = self.view.camera()
        camController = Qt3DExtras.QFirstPersonCameraController(self.rootEntity)
        camController.setCamera(cameraEntity)
        self.view.setRootEntity(self.rootEntity)

        self.material = Qt3DExtras.QPhongMaterial(self.rootEntity)

        self.add_sphere(20,5,5,5)

    def add_sphere(self, radius, x, y, z):

        self.sphereEntity = Qt3DCore.QEntity(self.rootEntity)
        self.sphereMesh = Qt3DExtras.QSphereMesh()
        self.sphereMesh.setRadius(radius)

        self.sphereTransform = Qt3DCore.QTransform()
        self.sphereTransform.setTranslation(QVector3D(x, y, z))

        self.sphereEntity.addComponent(self.sphereMesh)
        self.sphereEntity.addComponent(self.material)
        self.sphereEntity.addComponent(self.sphereTransform)

        print("Created sphere.")
