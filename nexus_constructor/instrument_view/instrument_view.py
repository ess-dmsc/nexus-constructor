import logging
import time
import typing
from copy import deepcopy
from typing import Dict, Tuple

from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QVector3D
from PySide6.QtWidgets import QVBoxLayout, QWidget

from nexus_constructor.common_attrs import SHAPE_GROUP_NAME
from nexus_constructor.component_type import (
    CHOPPER_CLASS_NAME,
    SLIT_CLASS_NAME,
    SOURCE_CLASS_NAME,
)
from nexus_constructor.geometry.disk_chopper.disk_chopper_checker import ChopperChecker
from nexus_constructor.geometry.disk_chopper.disk_chopper_geometry_creator import (
    DiskChopperGeometryCreator,
)
from nexus_constructor.geometry.slit.slit_geometry import SlitGeometry
from nexus_constructor.instrument_view.entity_collections import (
    EntityCollection,
    GroundEntityCollection,
    NeutronSourceEntityCollection,
    OffMeshEntityCollection,
)
from nexus_constructor.instrument_view.gnomon import Gnomon
from nexus_constructor.instrument_view.instrument_view_axes import InstrumentViewAxes
from nexus_constructor.instrument_view.instrument_zooming_3d_window import (
    InstrumentZooming3DWindow,
)
from nexus_constructor.instrument_view.off_renderer import OffMesh
from nexus_constructor.instrument_view.qentity_utils import create_material
from nexus_constructor.model.component import Component
from nexus_constructor.model.geometry import OFFGeometryNexus
from nexus_constructor.model.group import Group


def _set_chopper_geometry(component: Component):
    """
    Attempts to set a chopper geometry in the component by checking if the component fields describe a valid chopper.
    :param component: The component to be given a shape.
    """
    chopper_validator = ChopperChecker(component.children)
    if chopper_validator.validate_chopper():
        chopper_details = chopper_validator.chopper_details
        chopper_creator = DiskChopperGeometryCreator(chopper_details)
        component[SHAPE_GROUP_NAME] = chopper_creator.create_disk_chopper_geometry()
    else:
        logging.warning("Validation failed. Unable to create disk chopper mesh.")


def _set_slit_geometry(component: Component):
    slit_geometry = SlitGeometry(component)
    component.set_off_shape(slit_geometry.create_slit_geometry())


SPECIAL_SHAPE_CASES = {
    CHOPPER_CLASS_NAME: _set_chopper_geometry,
    SLIT_CLASS_NAME: _set_slit_geometry,
}


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

    def __init__(self, parent, main_window):
        super().__init__()

        self.main_window = main_window

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
        self.view = InstrumentZooming3DWindow(self.component_root_entity, main_window)
        self.view.defaultFrameGraph().setClearColor(QColor("lightgrey"))
        self.view.setRootEntity(self.root_entity)
        container = QWidget.createWindowContainer(self.view)
        lay.addWidget(container)

        self.default_camera_settings = {
            "perspective": [45, 16.0 / 9.0, 0.01, 1000],
            "position": QVector3D(6, 8, 30),
            "ortographic": [-20, 20, -20, 20, 0.01, 1000],
            "position_top": QVector3D(0, 5, 0),
            "position_side": QVector3D(5, 0, 0),
            "position_front": QVector3D(0, 0, -5),
            "viewcenter": QVector3D(0, 0, 0),
            "cameraspeed": 10,
        }
        self.current_camera_settings = deepcopy(self.default_camera_settings)
        self.camera_entity = self.view.camera()
        self.cam_controller = Qt3DExtras.QFirstPersonCameraController(self.root_entity)
        self.switch_to_perspective()

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
        self.component_entities: Dict[str, EntityCollection] = {}
        self.components: Dict[str, Component] = {}
        self.transformations = {}

        # Create layers in order to allow one camera to only see the gnomon and one camera to only see the
        # components and axis lines
        self.create_layers()
        self.initialise_view()

        # Create the ground layer
        self.create_ground()
        self.start_time = time.time()

        # Insert the beam cylinder last. This ensures that the semi-transparency works correctly.
        self.gnomon.setup_beam_cylinder()

        # Move the gnomon when the camera view changes
        self.view.camera().viewVectorChanged.connect(self.gnomon.update_gnomon)
        self.target_child = None

    def switch_to_perspective(self):
        """
        Method for setting camera perspective
        """
        # Set the properties of the instrument camera controller
        self.cam_controller.setLinearSpeed(self.current_camera_settings["cameraspeed"])
        self.cam_controller.setCamera(self.camera_entity)

        # Enable the camera to see a large distance by giving it a small nearView and large farView
        self.view.camera().lens().setPerspectiveProjection(
            *self.current_camera_settings["perspective"]
        )

        # Set the camera view centre as the origin and position the camera so that it looks down at the initial sample
        self.view.camera().setPosition(self.current_camera_settings["position"])

        self.view.camera().setViewCenter(self.current_camera_settings["viewcenter"])

    def create_ground(self):
        """
        Method for creating the ground entity
        """
        ground_component = GroundEntityCollection(self.component_root_entity)
        ground_component.create_entities()
        self.component_entities["_ground"] = ground_component

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

        # Make sure flat surfaces are rendered on both sides
        renderStateSet = Qt3DRender.QRenderStateSet(component_clear_buffers)
        m_CullFace = Qt3DRender.QCullFace(renderStateSet)
        m_CullFace.setMode(Qt3DRender.QCullFace.NoCulling)
        renderStateSet.addRenderState(m_CullFace)

        # Create a viewport for gnomon in small section of the screen
        self.gnomon_viewport = Qt3DRender.QViewport(surface_selector)
        self.update_gnomon_size()

        # Filter out the gnomon for just the gnomon camera to see
        self.gnomon_camera = self.gnomon.get_gnomon_camera()
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

    def add_component(self, component: Component):
        """
        Add a component to the instrument view.
        :param component: The component to add.
        """
        name, nx_class = component.absolute_path, component.nx_class
        geometry, positions = component.shape
        q_component: EntityCollection
        if geometry is None:
            return
        if nx_class in [CHOPPER_CLASS_NAME, SLIT_CLASS_NAME]:
            component = deepcopy(component)
            SPECIAL_SHAPE_CASES[nx_class](component)
            geometry, positions = component.shape
        if nx_class == SOURCE_CLASS_NAME:
            q_component = NeutronSourceEntityCollection(
                self.component_root_entity, nx_class
            )
        else:
            mesh = OffMesh(
                geometry.off_geometry, self.component_root_entity, positions, True
            )
            q_component = OffMeshEntityCollection(
                mesh, self.component_root_entity, nx_class
            )
        q_component.create_entities()
        self.component_entities[name] = q_component
        self.components[name] = component

        backend_use_simplified_mesh = False
        if backend_use_simplified_mesh and isinstance(geometry, OFFGeometryNexus):
            try:
                geometry.vertices, geometry.faces = mesh.simple_geometry
            except Exception:
                print("Failed to set simplified mesh to backend for {}".format(name))

    def update_meshes(self):
        """
        Switch from low-res meshes to high-res meshes, and vice versa
        """
        for name in self.component_entities.keys():
            if "_ground" in name:
                continue
            if not hasattr(self.component_entities[name], "_mesh"):
                continue
            for e in self.component_entities[name].entities:
                if isinstance(e, tuple):
                    e = e[0]
                component = self.components[name]
                geometry, positions = component.shape
                if e.old_mesh is not None:
                    new_mesh = e.old_mesh
                else:
                    new_mesh = OffMesh(
                        geometry.off_geometry,
                        self.component_root_entity,
                        positions,
                        True,
                        False,
                    )
                e.switch_mesh(new_mesh)

    def get_entity(self, component_name: str) -> Qt3DCore.QEntity:
        """
        Obtain the entity from the InstrumentView based on its name.
        """
        try:
            return self.component_entities[component_name].entity_to_zoom()
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
        Don't remove startup components
        """
        if time.time() - self.start_time < 1:
            return
        for component in self.component_entities.keys():
            self.component_entities[component].setParent(None)
        self.component_entities = dict()
        self.components = dict()

    def delete_component(self, name: str):
        """
        Delete a component from the InstrumentView by removing the components and entity from the dictionaries.
        :param name: The name of the component.
        """
        try:
            self.component_entities[name].setParent(None)
            self.component_entities.pop(name)
            self.components.pop(name)
        except KeyError:
            logging.error(
                f"Unable to delete component {name} because it doesn't exist."
            )
        try:
            self.transformations.pop(name)
        except KeyError:
            pass  # no problem if there are no transformations to remove

    @typing.no_type_check
    def select_component(self, name: str):
        """
        Method for when a component is pressed in the treeview
        """
        if time.time() - self.view.last_press_time < 0.1:
            return
        try:
            for key in self.component_entities.keys():
                entity = self.component_entities[key]
                for e in entity.entities:
                    if isinstance(e, tuple):
                        e = e[0]
                    if not e.hoover_material:
                        continue
                    try:
                        if key == name:
                            e.clicked = True
                            e.inside = False
                            e.switch_to_highlight()
                        else:
                            e.clicked = False
                            e.inside = False
                            e.switch_to_normal()
                    except Exception:
                        pass
        except KeyError:
            logging.error(
                f"Unable to select component {name} because it doesn't exist."
            )

    def iterate_tree(self, parent, target):
        if self.target_child or not isinstance(parent, Group):
            return
        for child in parent.children:
            if not isinstance(child, Group):
                continue
            if child.absolute_path == target:
                self.target_child = child
                break
            try:
                self.iterate_tree(child, target)
            except Exception:
                pass

    def select_entity(self, component: Component):
        """
        Method for when a component is pressed in the instrument view
        """
        for key in self.component_entities.keys():
            entity = self.component_entities[key]
            for e in entity.entities:
                if isinstance(e, tuple):
                    e = e[0]
                if e == component:
                    name = key

        component_tree_view = (
            self.main_window.component_tree_view_tab.component_tree_view
        )
        component_model = self.main_window.component_tree_view_tab.component_model
        selected = component_tree_view.selectedIndexes()
        if len(selected) == 0:
            return

        try:
            name_compare = (
                selected[0].internalPointer().name
                == selected[0].internalPointer().absolute_path.split("/")[1]
            )
        except Exception:
            name_compare = False
        if name_compare:
            root_index = selected[0].internalPointer()
        else:
            root_index = selected[0].data().parent_node
            while True:
                new_root_index = root_index.parent_node
                if new_root_index:
                    root_index = new_root_index
                elif new_root_index is None:
                    break

        self.target_child = None
        self.iterate_tree(root_index, name)
        new_selection_index = component_model.find_index_of_group(self.target_child)
        component_tree_view.setCurrentIndex(new_selection_index)

    def updateRenderedMaterials(self, material_name, color_state):
        for entity in self.component_root_entity.children():
            try:
                material_family = entity.material_family
                print(material_family)
            except Exception:
                continue

            if material_family == material_name:
                (
                    new_default_material,
                    new_hoover_material,
                    new_material_family,
                ) = create_material(
                    material_name,
                    self.root_entity,
                )
            for c in entity.components():
                if isinstance(
                    c,
                    (
                        Qt3DExtras.QPhongMaterial,
                        Qt3DExtras.QPhongAlphaMaterial,
                        Qt3DExtras.QGoochMaterial,
                    ),
                ):
                    entity.removeComponent(c)
            entity.addComponent(new_default_material)

    def add_transformation(self, component):
        """
        Add a transformation to a component, each component has a single transformation which contains
        the resultant transformation for its entire depends_on chain of translations and rotations
        """
        try:
            name, transformation = component.absolute_path, component.qtransform
            self.transformations[name] = transformation
            component = self.component_entities[name]
            component.add_transformation(transformation)
        except KeyError:
            pass

    def clear_all_transformations(self):
        """
        Remove all transformations from all components
        """
        for component_name, transformation in self.transformations.items():
            self.component_entities[component_name].remove_transformation(
                transformation
            )
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
