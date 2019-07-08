from typing import Tuple

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtCore import QRectF
from PySide2.QtGui import QVector3D, QColor
from PySide2.QtWidgets import QWidget, QVBoxLayout

from nexus_constructor.gnomon import Gnomon
from nexus_constructor.instrument_view_axes import InstrumentViewAxes
from nexus_constructor.instrument_zooming_3d_window import InstrumentZooming3DWindow
from nexus_constructor.off_renderer import OffMesh
from nexus_constructor.qentity_utils import (
    add_qcomponents_to_entity,
    set_material_properties,
)


class InstrumentView(QWidget):
    """
    Class for managing the 3D view in the NeXus Constructor. Creates the initial sample, the initial beam, and the
    neutron animation.
    :param parent: The MainWindow in which this widget is created. This isn't used for anything but is accepted as an
                   argument in order to appease Qt Designer.
    """

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

        # Set up view surface selector for filtering
        self.surface_selector = Qt3DRender.QRenderSurfaceSelector()
        self.surface_selector.setSurface(self.view)

        # Initialise materials
        self.grey_material = Qt3DExtras.QPhongMaterial()
        self.red_material = Qt3DExtras.QPhongMaterial()
        self.beam_material = Qt3DExtras.QPhongAlphaMaterial()

        # Initialise cube objects
        self.sample_cube_dimensions = [1, 1, 1]
        self.cube_entity = Qt3DCore.QEntity(self.component_root_entity)
        self.cube_mesh = Qt3DExtras.QCuboidMesh()

        # Create the gnomon resources and get its camera
        self.gnomon = Gnomon(
            self.gnomon_root_entity,
            self.view.camera(),
            self.beam_material,
            self.grey_material,
        )
        self.gnomon_camera = self.gnomon.get_gnomon_camera()

        # Create the axes lines objects
        self.instrument_view_axes = InstrumentViewAxes(
            self.axes_root_entity, self.view.camera().farPlane()
        )

        # Create layers in order to allow one camera to only see the gnomon and one camera to only see the
        # components and axis lines
        self.create_layers()
        self.initialise_view()

        # Dictionaries for component-related objects also to prevent them from going out of scope
        self.component_meshes = {}
        self.component_entities = {}
        self.component_transformations = {}

        # Insert the beam cylinder last. This ensures that the semi-transparency works correctly.
        self.gnomon.setup_beam_cylinder()

        # Move the gnomon when the camera view changes
        self.view.camera().viewVectorChanged.connect(self.gnomon.update_gnomon)

    def create_layers(self):
        """
        Assigns the gnomon view and component view to different cameras and viewports.
        """
        main_camera = self.view.camera()
        viewport = Qt3DRender.QViewport(self.surface_selector)
        self.view.setActiveFrameGraph(self.surface_selector)

        # Filters out just the instrument for the main camera to see
        component_clear_buffers = self.create_camera_filter(
            viewport, self.combined_component_axes_entity, main_camera
        )

        component_clear_buffers.setBuffers(Qt3DRender.QClearBuffers.AllBuffers)
        component_clear_buffers.setClearColor(QColor("lightgrey"))

        # Create a viewport for gnomon in small section of the screen
        self.gnomon_viewport = Qt3DRender.QViewport(self.surface_selector)
        self.update_gnomon_size()

        # Filter out the gnomon for just the gnomon camera to see
        self.create_camera_filter(
            self.gnomon_viewport, self.gnomon_root_entity, self.gnomon_camera
        )

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
    def create_camera_filter(viewport, visible_entity, camera_to_filter):
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

    def add_component(self, name, geometry):
        """
        Add a component to the instrument view given a name and its geometry.
        :param name: The name of the component.
        :param geometry: The geometry information of the component that is used to create a mesh.
        """
        entity = Qt3DCore.QEntity(self.component_root_entity)
        mesh = OffMesh(geometry.off_geometry)

        add_qcomponents_to_entity(entity, [mesh, self.grey_material])

        self.component_meshes[name] = mesh
        self.component_entities[name] = entity

    def delete_component(self, name):
        """
        Delete a component from the InstrumentView by removing the components and entity from the dictionaries.
        :param name: The name of the component.
        """

        self.component_entities[name].setParent(None)

        try:
            del self.component_entities[name]
            del self.component_meshes[name]
        except KeyError:
            print("Unable to delete component " + name + " because it doesn't exist.")

        self._delete_all_transformations(name)

    def _delete_all_transformations(self, component_name):
        """
        Deletes all the transformations associated with a component. Doesn't print a message in the case of a KeyError
        because components without transformations can exist.
        """
        try:
            del self.component_transformations[component_name]
        except KeyError:
            pass

    def add_transformation(self, component_name, transformation_name):
        pass

    def delete_single_transformation(self, component_name, transformation_name):
        pass

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

        set_material_properties(self.grey_material, black, grey)
        set_material_properties(self.red_material, red, dark_red)
        set_material_properties(self.beam_material, blue, light_blue, alpha=0.5)

    @staticmethod
    def set_cube_mesh_dimensions(cube_mesh, x, y, z):
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

    def setup_sample_cube(self):
        """
        Sets up the cube that represents a sample in the 3D view by giving the cube entity a mesh and a material.
        """
        self.set_cube_mesh_dimensions(self.cube_mesh, *self.sample_cube_dimensions)
        add_qcomponents_to_entity(self.cube_entity, [self.cube_mesh, self.red_material])

    def initialise_view(self):
        """
        Calls the methods for defining materials, setting up the sample cube, and setting up the neutrons. Beam-related
        functions are called outside of this method to ensure that those things are generated last.
        """
        self.give_colours_to_materials()
        self.setup_sample_cube()
        self.gnomon.create_gnomon()
        self.gnomon.setup_neutrons()
