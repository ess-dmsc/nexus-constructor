from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtCore import QPropertyAnimation, QRectF
from PySide2.QtGui import QVector3D, QColor, QMatrix4x4, QFont
from PySide2.Qt3DRender import Qt3DRender
from ui.NeutronAnimationController import NeutronAnimationController


class InstrumentView(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        self.view = Qt3DExtras.Qt3DWindow()
        # self.view.defaultFrameGraph().setClearColor(QColor("lightgrey"))
        container = QWidget.createWindowContainer(self.view)
        lay.addWidget(container)

        self.view.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
        self.view.camera().setPosition(QVector3D(6, 8, 30))
        self.view.camera().setViewCenter(QVector3D(0, 0, 0))

        self.rootEntity = Qt3DCore.QEntity()

        self.componentRootEntity = Qt3DCore.QEntity(self.rootEntity)

        self.gnomonRootEntity = Qt3DCore.QEntity(self.rootEntity)

        self.view.setRootEntity(self.rootEntity)

        self.create_layers()
        self.initialise_view()

    def create_layers(self):

        self.surSelector = Qt3DRender.QRenderSurfaceSelector()
        self.surSelector.setSurface(self.view)
        self.viewportComponent = Qt3DRender.QViewport(self.surSelector)

        self.view.setActiveFrameGraph(self.surSelector)


        self.componentLayerFilter = Qt3DRender.QLayerFilter(self.viewportComponent)
        self.componentLayer = Qt3DRender.QLayer(self.componentRootEntity)
        self.componentRootEntity.addComponent(self.componentLayer)
        self.componentLayer.setRecursive(True)
        self.componentLayerFilter.addLayer(self.componentLayer)

        componentCameraEntity = self.view.camera()
        componentCamController = Qt3DExtras.QFirstPersonCameraController(self.componentRootEntity)
        componentCamController.setLinearSpeed(20)
        componentCamController.setCamera(componentCameraEntity)

        self.componentCameraSelector = Qt3DRender.QCameraSelector(self.componentLayerFilter)
        self.componentCameraSelector.setCamera(self.view.camera())
        self.componentClearBuffers = Qt3DRender.QClearBuffers(self.componentCameraSelector)
        self.componentClearBuffers.setBuffers(Qt3DRender.QClearBuffers.AllBuffers)
        self.componentClearBuffers.setClearColor(QColor("lightgrey"))

        self.viewportGnomon = Qt3DRender.QViewport(self.surSelector)
        self.viewportGnomon.setNormalizedRect(QRectF(0.8,0.8,0.2,0.2))
        self.layerFilterGnomon = Qt3DRender.QLayerFilter(self.viewportGnomon)
        self.gnomonLayer = Qt3DRender.QLayer(self.gnomonRootEntity)
        self.gnomonRootEntity.addComponent(self.gnomonLayer)
        self.gnomonLayer.setRecursive(True)
        self.layerFilterGnomon.addLayer(self.gnomonLayer)
        self.cameraSelectorGnomon = Qt3DRender.QCameraSelector(self.layerFilterGnomon)
        self.clearBuffersGnomon = Qt3DRender.QClearBuffers(self.cameraSelectorGnomon)

        self.gnomonCameraEntity = Qt3DRender.QCamera()
        self.gnomonCameraEntity.setParent(self.gnomonRootEntity)
        self.gnomonCameraEntity.setProjectionType(componentCameraEntity.projectionType())
        self.gnomonCameraEntity.setFieldOfView(componentCameraEntity.fieldOfView())
        self.gnomonCameraEntity.setNearPlane(0.1)
        self.gnomonCameraEntity.setFarPlane(10)
        self.gnomonCameraEntity.setUpVector(componentCameraEntity.upVector())
        self.gnomonCameraEntity.setViewCenter(QVector3D(0, 0, 0))
        # self.otherCamera.setTop(2)

        # self.otherCamera.setFarPlane(10)
        gnomonCamPosition = componentCameraEntity.position() - componentCameraEntity.viewCenter()
        gnomonCamPosition = gnomonCamPosition.normalized()
        gnomonCamPosition *= 3

        print(gnomonCamPosition)
        self.gnomonCameraEntity.setPosition(gnomonCamPosition)

        # self.otherCamera.setPosition(QVector3D(0,0,0.0001))

        gnomonCamController = Qt3DExtras.QOrbitCameraController(self.gnomonRootEntity)
        gnomonCamController.setZoomInLimit(1)
        gnomonCamController.setAcceleration(0)
        gnomonCamController.setDeceleration(0)
        # gnomonCamController.setLinearSpeed(0)
        # gnomonCamController.setLookSpeed(0)
        # gnomonCamController.set
        gnomonCamController.setCamera(self.gnomonCameraEntity)

        print(componentCamController.linearSpeed())

        self.cameraSelectorGnomon.setCamera(self.gnomonCameraEntity)

        self.clearBuffersGnomon.setBuffers(Qt3DRender.QClearBuffers.DepthBuffer)
        # self.clearBuffersGnomon.setBuffers(Qt3DRender.QClearBuffers.LessOr)


    def create_materials(self):

        red = QColor("red")
        green = QColor("green")
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

        self.cubeEntity = Qt3DCore.QEntity(self.componentRootEntity)
        self.cubeMesh = Qt3DExtras.QCuboidMesh()
        self.cubeMesh.setXExtent(1)
        self.cubeMesh.setYExtent(1)
        self.cubeMesh.setZExtent(1)

        self.cubeEntity.addComponent(self.cubeMesh)
        self.cubeEntity.addComponent(self.red_material)

    def create_beam_cylinder(self):

        self.cylinderEntity = Qt3DCore.QEntity(self.componentRootEntity)
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

    def gnomon_cube(self):

        self.gnomonCubeEntity = Qt3DCore.QEntity(self.gnomonRootEntity)
        self.gnomonCubeMesh = Qt3DExtras.QCuboidMesh()
        self.gnomonCubeMesh.setXExtent(1)
        self.gnomonCubeMesh.setYExtent(1)
        self.gnomonCubeMesh.setZExtent(1)

        self.gnomonCubeEntity.addComponent(self.gnomonCubeMesh)
        self.gnomonCubeEntity.addComponent(self.red_material)

    def add_gnomon(self):


        self.xAxisEntity = Qt3DCore.QEntity(self.gnomonRootEntity)
        self.yAxisEntity = Qt3DCore.QEntity(self.gnomonRootEntity)
        self.zAxisEntity = Qt3DCore.QEntity(self.gnomonRootEntity)

        self.xAxisMesh = Qt3DExtras.QCylinderMesh()
        self.yAxisMesh = Qt3DExtras.QCylinderMesh()
        self.zAxisMesh = Qt3DExtras.QCylinderMesh()

        self.xAxisMesh.setRadius(0.025)
        self.yAxisMesh.setRadius(0.025)
        self.zAxisMesh.setRadius(0.025)

        self.xAxisMesh.setLength(1)
        self.yAxisMesh.setLength(1)
        self.zAxisMesh.setLength(1)

        self.xAxisMesh.setRings(2)
        self.yAxisMesh.setRings(2)
        self.zAxisMesh.setRings(2)

        xAxisMatrix = QMatrix4x4()
        yAxisMatrix = QMatrix4x4()
        zAxisMatrix = QMatrix4x4()

        xAxisMatrix.rotate(270, QVector3D(0,0,1))
        xAxisMatrix.translate(QVector3D(0, 0.5, 0))

        yAxisMatrix.translate(QVector3D(0, 0.5, 0))

        zAxisMatrix.rotate(90, QVector3D(1, 0, 0))
        zAxisMatrix.translate(QVector3D(0, 0.5, 0))

        self.xAxisTransformation = Qt3DCore.QTransform()
        self.yAxisTransformation = Qt3DCore.QTransform()
        self.zAxisTransformation = Qt3DCore.QTransform()

        self.xAxisTransformation.setMatrix(xAxisMatrix)
        self.yAxisTransformation.setMatrix(yAxisMatrix)
        self.zAxisTransformation.setMatrix(zAxisMatrix)

        self.xAxisEntity.addComponent(self.xAxisMesh)
        self.xAxisEntity.addComponent(self.xAxisTransformation)
        self.xAxisEntity.addComponent(self.red_material)

        self.yAxisEntity.addComponent(self.yAxisMesh)
        self.yAxisEntity.addComponent(self.yAxisTransformation)
        self.yAxisEntity.addComponent(self.red_material)

        self.zAxisEntity.addComponent(self.zAxisMesh)
        self.zAxisEntity.addComponent(self.zAxisTransformation)
        self.zAxisEntity.addComponent(self.red_material)


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

            neutronEntity = Qt3DCore.QEntity(self.componentRootEntity)
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

    def create_gnomon(self):
        pass

    def initialise_view(self):

        self.create_materials()
        self.create_sample_cube()
        self.create_neutrons()
        self.add_gnomon()

        # The beam must be the last thing placed in the view in order to make the semi-transparency work correctly
        self.create_beam_cylinder()

        # self.create_gnomon()
