import logging
from typing import List, Tuple, Union

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtCore import QRectF
from PySide2.QtGui import QColor, QVector3D
from PySide2.QtWidgets import QVBoxLayout, QWidget

from nexus_constructor.component_type import SAMPLE_CLASS_NAME, SOURCE_CLASS_NAME
from nexus_constructor.instrument_view.gnomon import Gnomon
from nexus_constructor.instrument_view.instrument_view_axes import InstrumentViewAxes
from nexus_constructor.instrument_view.instrument_zooming_3d_window import (
    InstrumentZooming3DWindow,
)
from nexus_constructor.instrument_view.off_renderer import OffMesh
from nexus_constructor.instrument_view.qentity_utils import (  # create_neutron_source,
    QSource,
    create_material,
    create_qentity,
)
from nexus_constructor.model.geometry import (
    CylindricalGeometry,
    NoShapeGeometry,
    OFFGeometryNexus,
)


class InstrumentView(QWidget):
    """
    Class for managing the 3D view in the NeXus Constructor. Creates the initial sample, the initial beam, and the
    neutron animation.
    :param parent: The MainWindow in which this widget is created. This isn't used for anything but is accepted as an
                   argument in order to appease Qt Designer.
    """

    def delete(self):
        """
        Fixes Qt3D segfault - this needs to be called when the program closes otherwise Qt tries to draw objects as python is cleaning them up.
        """
        self.clear_all_components()
        del self.root_entity
        del self.view

    def __init__(self, parent):
        super().__init__()

        self.root_entity = Qt3DCore.QEntity()

        # Make additional entities for the gnomon and instrument components
        self.combined_component_axes_entity = Qt3DCore.QEntity(self.root_entity)
        self.component_root_entity = Qt3DCore.QEntity(
            self.combined_component_axes_entity
        )
        self.axes_root_entity = Qt3DCore.QEntity(self.combined_component_axes_entity)
        self.gnomon_root_entity = Qt3DCore.QEntity(self.root_entity)

        # Create the 3DWindow and place it in a widget with a layout
        lay = QVBoxLayout(self)
        self.view = InstrumentZooming3DWindow(self.component_root_entity)
        self.view.defaultFrameGraph().setClearColor(QColor("lightgrey"))
        self.view.setRootEntity(self.root_entity)
        container = QWidget.createWindowContainer(self.view)
        lay.addWidget(container)

        # Set the properties of the instrument camera controller
        camera_entity = self.view.camera()
        cam_controller = Qt3DExtras.QFirstPersonCameraController(self.root_entity)
        cam_controller.setLinearSpeed(20)
        cam_controller.setCamera(camera_entity)

        # Enable the camera to see a large distance by giving it a small nearView and large farView
        self.view.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.01, 1000)

        # Set the camera view centre as the origin and position the camera so that it looks down at the initial sample
        self.view.camera().setPosition(QVector3D(6, 8, 30))
        self.view.camera().setViewCenter(QVector3D(0, 0, 0))

        # Make sure that the size of the gnomon stays the same when the 3D view is resized
        self.view.heightChanged.connect(self.update_gnomon_size)
        self.view.widthChanged.connect(self.update_gnomon_size)

        # Keep a reference to the gnomon viewport so that it can be resized to preserve the original size of the gnomon
        self.gnomon_viewport = None

        # Choose a fixed height and width for the gnomon so that this can be preserved when the 3D view is resized
        self.gnomon_height = self.gnomon_width = 140

        # Create the gnomon resources
        self.gnomon = Gnomon(self.gnomon_root_entity, self.view.camera())

        # Create the axes lines objects
        InstrumentViewAxes(self.axes_root_entity, self.view.camera().farPlane())

        # Dictionary of components and transformations so that we can delete them later
        self.component_entities = {}
        self.transformations = {}

        # Create layers in order to allow one camera to only see the gnomon and one camera to only see the
        # components and axis lines
        self.create_layers()
        self.initialise_view()

        # Insert the beam cylinder last. This ensures that the semi-transparency works correctly.
        self.gnomon.setup_beam_cylinder()

        # Move the gnomon when the camera view changes
        self.view.camera().viewVectorChanged.connect(self.gnomon.update_gnomon)

    def create_layers(self):
        """
        Assigns the gnomon view and component view to different cameras and viewports. Controls the buffer behaviour of
        the different viewports so that the depth buffer behaves in such a way that the gnomon is always in front.
        """
        # Set up view surface selector for filtering
        surface_selector = Qt3DRender.QRenderSurfaceSelector(self.root_entity)
        surface_selector.setSurface(self.view)

        main_camera = self.view.camera()
        viewport = Qt3DRender.QViewport(surface_selector)
        self.view.setActiveFrameGraph(surface_selector)

        # Filters out just the instrument for the main camera to see
        component_clear_buffers = self.create_camera_filter(
            viewport, self.combined_component_axes_entity, main_camera
        )

        # Have the component buffer take on the default behaviour
        component_clear_buffers.setBuffers(Qt3DRender.QClearBuffers.AllBuffers)

        # Set the background color of the main scene
        component_clear_buffers.setClearColor(QColor("lightgrey"))

        # Create a viewport for gnomon in small section of the screen
        self.gnomon_viewport = Qt3DRender.QViewport(surface_selector)
        self.update_gnomon_size()

        # Filter out the gnomon for just the gnomon camera to see
        gnomon_camera = self.gnomon.get_gnomon_camera()
        gnomon_clear_buffers = self.create_camera_filter(
            self.gnomon_viewport, self.gnomon_root_entity, gnomon_camera
        )
        # Make the gnomon appear in front of everything else
        gnomon_clear_buffers.setBuffers(Qt3DRender.QClearBuffers.DepthBuffer)

        self.gnomon.update_gnomon()

    def update_gnomon_size(self):
        """
        Ensures that the gnomon retains its size when the size of the 3D view has been changed. Calculates the desired
        gnomon size as a proportion of the current window size and passes these values to the gnomon viewport.
        """
        height_ratio, width_ratio = self.calculate_gnomon_rect(
            self.view.height(), self.view.width(), self.gnomon_height, self.gnomon_width
        )
        self.gnomon_viewport.setNormalizedRect(
            QRectF(1 - width_ratio, 1 - height_ratio, width_ratio, height_ratio)
        )

    @staticmethod
    def calculate_gnomon_rect(
        view_height: float, view_width: float, gnomon_height: float, gnomon_width: float
    ) -> Tuple[float, float]:
        """
        Finds the ratio of the desired gnomon height/width to the current 3D view height/width.
        :param view_height: The current 3D view height.
        :param view_width: The current 3D view width.
        :param gnomon_height: The desired gnomon height.
        :param gnomon_width: The desired gnomon width.
        :return: The gnomon height/width ratios that are required to determine the size of the gnomon viewport.
        """
        height_ratio = gnomon_height / view_height
        width_ratio = gnomon_width / view_width
        return height_ratio, width_ratio

    @staticmethod
    def create_camera_filter(
        viewport: Qt3DRender.QViewport,
        visible_entity: Qt3DCore.QEntity,
        camera_to_filter: Qt3DRender.QCamera,
    ) -> Qt3DRender.QClearBuffers:
        """
        Filter the objects that are visible to a camera.
        :param viewport: The viewport that the camera is using.
        :param visible_entity: Only children of this entity will be visible to the camera.
        :param camera_to_filter: The camera to apply the filter to.
        :return: The clear buffers
        """
        layer_filter = Qt3DRender.QLayerFilter(viewport)
        layer = Qt3DRender.QLayer(visible_entity)
        visible_entity.addComponent(layer)
        layer.setRecursive(True)
        layer_filter.addLayer(layer)
        camera_selector = Qt3DRender.QCameraSelector(layer_filter)
        camera_selector.setCamera(camera_to_filter)
        clear_buffers = Qt3DRender.QClearBuffers(camera_selector)
        return clear_buffers

    def add_component(
        self,
        name: str,
        nx_class,
        geometry: Union[NoShapeGeometry, CylindricalGeometry, OFFGeometryNexus],
        positions: List[QVector3D] = None,
    ):
        """
        Add a component to the instrument view given a name and its geometry.
        :param name: The name of the component.
        :param geometry: The geometry information of the component that is used to create a mesh.
        :param positions: Mesh is repeated at each of these positions
        """
        print(name, nx_class)
        if geometry is None:
            return

        if nx_class == SOURCE_CLASS_NAME:
            entity = QSource(self.component_root_entity)
            entity.create_neutron_source()
            self.component_entities[name] = entity
        else:
            mesh = OffMesh(geometry.off_geometry, self.component_root_entity, positions)
            material = create_material(
                QColor("black") if nx_class != SAMPLE_CLASS_NAME else QColor("red"),
                QColor("grey"),
                self.component_root_entity,
                alpha=0.5 if nx_class == SAMPLE_CLASS_NAME else None,
            )
            self.component_entities[name] = create_qentity(
                [mesh, material], self.component_root_entity
            )

    def get_entity(self, component_name: str) -> Qt3DCore.QEntity:
        """
        Obtain the entity from the InstrumentView based on its name.
        """
        try:
            return self.component_entities[component_name]
        except KeyError:
            logging.error(
                f"Unable to retrieve component {component_name} because it doesn't exist."
            )

    @staticmethod
    def zoom_to_component(entity: Qt3DCore.QEntity, camera: Qt3DRender.QCamera):
        """
        Instructs a camera to zoom in on an individual component.
        :param entity: The component entity that the camera should zoom in on.
        :param camera: The camera that will do the zooming.
        """
        camera.viewEntity(entity)

    def clear_all_components(self):
        """
        resets the entities in qt3d so all components are cleared from the 3d view.
        """
        for component in self.component_entities.keys():
            self.component_entities[component].setParent(None)
        self.component_entities = dict()

    def delete_component(self, name: str):
        """
        Delete a component from the InstrumentView by removing the components and entity from the dictionaries.
        :param name: The name of the component.
        """
        try:
            self.component_entities[name].setParent(None)
            self.component_entities.pop(name)
        except KeyError:
            logging.error(
                f"Unable to delete component {name} because it doesn't exist."
            )
        try:
            self.transformations.pop(name)
        except KeyError:
            pass  # no problem if there are no transformations to remove

    def add_transformation(
        self, component_name: str, transformation: Qt3DCore.QTransform
    ):
        """
        Add a transformation to a component, each component has a single transformation which contains
        the resultant transformation for its entire depends_on chain of translations and rotations
        """
        self.transformations[component_name] = transformation
        component = self.component_entities[component_name]
        component.addComponent(transformation)

    def clear_all_transformations(self):
        """
        Remove all transformations from all components
        """
        for component_name, transformation in self.transformations.items():
            self.component_entities[component_name].removeComponent(transformation)
        self.transformations = {}

    @staticmethod
    def set_cube_mesh_dimensions(
        cube_mesh: Qt3DExtras.QCuboidMesh, x: float, y: float, z: float
    ):
        """
        Sets the dimensions of a cube mesh.
        :param cube_mesh: The cube mesh to modify.
        :param x: The desired x extent.
        :param y: The desired y extent.
        :param z: The desired z extent.
        """
        cube_mesh.setXExtent(x)
        cube_mesh.setYExtent(y)
        cube_mesh.setZExtent(z)

    def initialise_view(self):
        """
        Calls the methods for defining materials, setting up the sample cube, and setting up the neutrons. Beam-related
        functions are called outside of this method to ensure that those things are generated last.
        """
        self.gnomon.create_gnomon()
        self.gnomon.setup_neutrons()
