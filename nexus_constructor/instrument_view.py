from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtCore import QPropertyAnimation, QRectF
from PySide2.QtGui import QVector3D, QColor, QMatrix4x4, QFont, QVector4D
from nexus_constructor.neutron_animation_controller import NeutronAnimationController
from nexus_constructor.off_renderer import OffMesh


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

        # Set up view surface selector for filtering
        self.surface_selector = Qt3DRender.QRenderSurfaceSelector()
        self.surface_selector.setSurface(self.view)

        # Enable the camera to see a large distance by giving it a small nearView and large farView
        self.view.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.01, 1000)

        # Set the camera view centre as the origin and position the camera so that it looks down at the neutron beam
        self.view.camera().setPosition(QVector3D(6, 8, 30))
        self.view.camera().setViewCenter(QVector3D(0, 0, 0))

        self.root_entity = Qt3DCore.QEntity()
        camera_entity = self.view.camera()
        cam_controller = Qt3DExtras.QFirstPersonCameraController(self.root_entity)
        cam_controller.setLinearSpeed(20)
        cam_controller.setCamera(camera_entity)
        self.view.setRootEntity(self.root_entity)

        # Make additional cameras for the gnomon and the instrument components
        self.component_root_entity = Qt3DCore.QEntity(self.root_entity)
        self.gnomon_root_entity = Qt3DCore.QEntity(self.root_entity)
        self.gnomon_camera = self.create_gnomon_camera(self.view.camera())

        # Initialise materials
        self.grey_material = Qt3DExtras.QPhongMaterial()
        self.red_material = Qt3DExtras.QPhongMaterial()
        self.beam_material = Qt3DExtras.QPhongAlphaMaterial()
        self.x_material = Qt3DExtras.QPhongMaterial()
        self.y_material = Qt3DExtras.QPhongMaterial()
        self.z_material = Qt3DExtras.QPhongMaterial()

        # Initialise cube objects
        self.sample_cube_dimensions = [1, 1, 1]
        self.cube_entity = Qt3DCore.QEntity(self.component_root_entity)
        self.cube_mesh = Qt3DExtras.QCuboidMesh()

        self.num_neutrons = 9

        # Create a dictionary for neutron-related objects so that they are always in scope and not destroyed by C++
        self.neutron_objects = {
            "entities": [],
            "meshes": [],
            "transforms": [],
            "animation_controllers": [],
            "animations": [],
        }

        for _ in range(self.num_neutrons):
            self.neutron_objects["entities"].append(
                Qt3DCore.QEntity(self.component_root_entity)
            )
            self.neutron_objects["meshes"].append(Qt3DExtras.QSphereMesh())
            self.neutron_objects["transforms"].append(Qt3DCore.QTransform())

        self.cylinder_length = 40

        # Gnomon resources

        self.gnomon_cylinder_length = 4

        self.x_axis_entity = Qt3DCore.QEntity(self.gnomon_root_entity)
        self.y_axis_entity = Qt3DCore.QEntity(self.gnomon_root_entity)
        self.z_axis_entity = Qt3DCore.QEntity(self.gnomon_root_entity)

        self.x_axis_mesh = Qt3DExtras.QCylinderMesh()
        self.y_axis_mesh = Qt3DExtras.QCylinderMesh()
        self.z_axis_mesh = Qt3DExtras.QCylinderMesh()

        self.x_axis_transformation = Qt3DCore.QTransform()
        self.y_axis_transformation = Qt3DCore.QTransform()
        self.z_axis_transformation = Qt3DCore.QTransform()

        self.x_cone_entity = Qt3DCore.QEntity(self.gnomon_root_entity)
        self.y_cone_entity = Qt3DCore.QEntity(self.gnomon_root_entity)
        self.z_cone_entity = Qt3DCore.QEntity(self.gnomon_root_entity)

        self.x_cone_mesh = Qt3DExtras.QConeMesh(self.gnomon_root_entity)
        self.y_cone_mesh = Qt3DExtras.QConeMesh(self.gnomon_root_entity)
        self.z_cone_mesh = Qt3DExtras.QConeMesh(self.gnomon_root_entity)

        self.x_cone_transformation = Qt3DCore.QTransform()
        self.y_cone_transformation = Qt3DCore.QTransform()
        self.z_cone_transformation = Qt3DCore.QTransform()

        self.x_axis_text = Qt3DExtras.QText2DEntity(self.gnomon_root_entity)
        self.y_axis_text = Qt3DExtras.QText2DEntity(self.gnomon_root_entity)
        self.z_axis_text = Qt3DExtras.QText2DEntity(self.gnomon_root_entity)

        self.x_text_transformation = Qt3DCore.QTransform()
        self.y_text_transformation = Qt3DCore.QTransform()
        self.z_text_transformation = Qt3DCore.QTransform()

        text_translation = self.gnomon_cylinder_length * 1.3

        self.x_text_vector = QVector3D(text_translation, -0.5, 0)
        self.y_text_vector = QVector3D(-0.4, text_translation, 0)
        self.z_text_vector = QVector3D(-0.5, -0.5, text_translation)

        self.create_layers()
        self.initialise_view()

        # Initialise beam objects
        self.cylinder_entity = Qt3DCore.QEntity(self.component_root_entity)
        self.cylinder_mesh = Qt3DExtras.QCylinderMesh()
        self.cylinder_transform = Qt3DCore.QTransform()

        # Dictionaries for component-related objects also to prevent them from going out of scope
        self.component_meshes = {}
        self.component_entities = {}
        self.component_transformations = {}

        # Insert the beam cylinder last. This ensures that the semi-transparency works correctly.
        self.setup_beam_cylinder()

        # Move the gnomon when the camera view changes
        self.view.camera().viewVectorChanged.connect(self.update_gnomon)

    @staticmethod
    def configure_gnomon_cylinder(cylinder_mesh, length):
        """
        Set the radius, length and ring properties of the cylinders that create the gnomon. The radius is 1/20th of the
        length and the number of rings is set to the smallest value that still creates the expected shape.
        :param cylinder_mesh: The mesh to be configured.
        :param length: The desired length of the cylinder.
        """
        cylinder_mesh.setRadius(length * 0.05)
        cylinder_mesh.setLength(length)
        cylinder_mesh.setRings(2)

    @staticmethod
    def create_cylinder_matrices(length):
        """
        Construct the matrices that are used to transform the cylinders so that they form a gnomon.
        :param length: The length of the cylinders.
        :return: The transformation matrices.
        """
        x_axis_matrix = QMatrix4x4()
        y_axis_matrix = QMatrix4x4()
        z_axis_matrix = QMatrix4x4()

        half_length = length * 0.5

        x_axis_matrix.rotate(270, QVector3D(0, 0, 1))
        x_axis_matrix.translate(QVector3D(0, half_length, 0))

        y_axis_matrix.translate(QVector3D(0, half_length, 0))

        z_axis_matrix.rotate(90, QVector3D(1, 0, 0))
        z_axis_matrix.translate(QVector3D(0, half_length, 0))

        return x_axis_matrix, y_axis_matrix, z_axis_matrix

    @staticmethod
    def create_cone_matrices(length):
        """
        Creates the matrices used to transform the cones that form the gnomon.
        :param length: The length of the gnomon cylinders.
        :return: The transformation matrices.
        """
        x_axis_matrix = QMatrix4x4()
        y_axis_matrix = QMatrix4x4()
        z_axis_matrix = QMatrix4x4()

        x_axis_matrix.rotate(270, QVector3D(0, 0, 1))
        x_axis_matrix.translate(QVector3D(0, length, 0))

        y_axis_matrix.translate(QVector3D(0, length, 0))

        z_axis_matrix.rotate(90, QVector3D(1, 0, 0))
        z_axis_matrix.translate(QVector3D(0, length, 0))

        return x_axis_matrix, y_axis_matrix, z_axis_matrix

    @staticmethod
    def create_axis_label_matrices(vectors):
        """
        Creates the matrices used to transform the labels that form the gnomon.
        :param vectors: The vectors that describe the location of the text.
        :return: The transformation matrices.
        """
        x_axis_matrix = QMatrix4x4()
        y_axis_matrix = QMatrix4x4()
        z_axis_matrix = QMatrix4x4()

        x_axis_matrix.translate(vectors[0])
        y_axis_matrix.translate(vectors[1])
        z_axis_matrix.translate(vectors[2])

        return x_axis_matrix, y_axis_matrix, z_axis_matrix

    @staticmethod
    def configure_gnomon_cone(cone_mesh, gnomon_cylinder_length):

        cone_mesh.setLength(gnomon_cylinder_length * 0.3)
        cone_mesh.setBottomRadius(gnomon_cylinder_length * 0.1)
        cone_mesh.setTopRadius(0)

    def create_gnomon(self):

        self.create_gnomon_cylinders()
        self.create_gnomon_cones()
        self.create_gnomon_text()

    def create_gnomon_text(self):
        self.set_axis_label_text(self.x_axis_text, "X", "red")
        self.set_axis_label_text(self.y_axis_text, "Y", "green")
        self.set_axis_label_text(self.z_axis_text, "Z", "blue")
        x_label_matrix, y_label_matrix, z_label_matrix = self.create_axis_label_matrices(
            [self.x_text_vector, self.y_text_vector, self.z_text_vector]
        )

        self.x_text_transformation.setMatrix(x_label_matrix)
        self.y_text_transformation.setMatrix(y_label_matrix)
        self.z_text_transformation.setMatrix(z_label_matrix)

        self.x_axis_text.addComponent(self.x_text_transformation)
        self.y_axis_text.addComponent(self.y_text_transformation)
        self.z_axis_text.addComponent(self.z_text_transformation)

    def create_gnomon_cones(self):
        self.configure_gnomon_cone(self.x_cone_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cone(self.y_cone_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cone(self.z_cone_mesh, self.gnomon_cylinder_length)
        x_cone_matrix, y_cone_matrix, z_cone_matrix = self.create_cone_matrices(
            self.gnomon_cylinder_length
        )
        self.x_cone_transformation.setMatrix(x_cone_matrix)
        self.y_cone_transformation.setMatrix(y_cone_matrix)
        self.z_cone_transformation.setMatrix(z_cone_matrix)
        self.add_qcomponents_to_entity(
            self.x_cone_entity,
            [self.x_cone_mesh, self.x_cone_transformation, self.x_material],
        )
        self.add_qcomponents_to_entity(
            self.y_cone_entity,
            [self.y_cone_mesh, self.y_cone_transformation, self.y_material],
        )
        self.add_qcomponents_to_entity(
            self.z_cone_entity,
            [self.z_cone_mesh, self.z_cone_transformation, self.z_material],
        )

    def create_gnomon_cylinders(self):

        self.configure_gnomon_cylinder(self.x_axis_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cylinder(self.y_axis_mesh, self.gnomon_cylinder_length)
        self.configure_gnomon_cylinder(self.z_axis_mesh, self.gnomon_cylinder_length)
        x_axis_matrix, y_axis_matrix, z_axis_matrix = self.create_cylinder_matrices(
            self.gnomon_cylinder_length
        )
        self.x_axis_transformation.setMatrix(x_axis_matrix)
        self.y_axis_transformation.setMatrix(y_axis_matrix)
        self.z_axis_transformation.setMatrix(z_axis_matrix)
        self.add_qcomponents_to_entity(
            self.x_axis_entity,
            [self.x_axis_mesh, self.x_axis_transformation, self.x_material],
        )
        self.add_qcomponents_to_entity(
            self.y_axis_entity,
            [self.y_axis_mesh, self.y_axis_transformation, self.y_material],
        )
        self.add_qcomponents_to_entity(
            self.z_axis_entity,
            [self.z_axis_mesh, self.z_axis_transformation, self.z_material],
        )

    @staticmethod
    def set_axis_label_text(text_entity, text_label, color):

        text_entity.setText(text_label)
        text_entity.setHeight(1.2)
        text_entity.setWidth(1)
        text_entity.setColor(QColor(color))
        text_entity.setFont(QFont("Courier New", 1))

    def create_layers(self):
        """
        Assigns the gnomon view and component view to different cameras and viewports.
        """
        main_camera = self.view.camera()
        viewport = Qt3DRender.QViewport(self.surface_selector)
        self.view.setActiveFrameGraph(self.surface_selector)

        # Filters out just the instrument for the main camera to see
        component_clear_buffers = self.create_camera_filter(
            viewport, self.component_root_entity, main_camera
        )

        component_clear_buffers.setBuffers(Qt3DRender.QClearBuffers.AllBuffers)
        component_clear_buffers.setClearColor(QColor("lightgrey"))

        gnomon_size = 0.2
        gnomon_start = 1 - gnomon_size

        # Create a viewport for gnomon in small section of the screen
        gnomon_viewport = Qt3DRender.QViewport(self.surface_selector)
        gnomon_viewport.setNormalizedRect(
            QRectF(gnomon_start, gnomon_start, gnomon_size, gnomon_size)
        )

        # Filter out the gnomon for just the gnomon camera to see
        self.create_camera_filter(
            gnomon_viewport, self.gnomon_root_entity, self.gnomon_camera
        )

        self.update_gnomon()

    def create_gnomon_camera(self, main_camera):
        gnomon_camera = Qt3DRender.QCamera()
        gnomon_camera.setParent(self.gnomon_root_entity)
        gnomon_camera.setProjectionType(main_camera.projectionType())
        gnomon_camera.lens().setPerspectiveProjection(
            main_camera.fieldOfView(), 1, 0.1, 25
        )
        gnomon_camera.setUpVector(main_camera.upVector())
        gnomon_camera.setViewCenter(QVector3D(0, 0, 0))
        return gnomon_camera

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

    def update_gnomon(self):

        self.update_gnomon_camera()
        self.update_gnomon_text()

    def update_gnomon_camera(self):
        main_camera = self.view.camera()

        updated_gnomon_camera_position = (
            main_camera.position() - main_camera.viewCenter()
        )
        updated_gnomon_camera_position = updated_gnomon_camera_position.normalized()
        updated_gnomon_camera_position *= self.gnomon_cylinder_length * 4

        self.gnomon_camera.setPosition(updated_gnomon_camera_position)
        self.gnomon_camera.setUpVector(self.view.camera().upVector())

    def update_gnomon_text(self):
        view_matrix = self.gnomon_camera.viewMatrix()
        self.x_text_transformation.setMatrix(
            self.create_billboard_transformation(view_matrix, self.x_text_vector)
        )
        self.y_text_transformation.setMatrix(
            self.create_billboard_transformation(view_matrix, self.y_text_vector)
        )
        self.z_text_transformation.setMatrix(
            self.create_billboard_transformation(view_matrix, self.z_text_vector)
        )

    @staticmethod
    def create_billboard_transformation(view_matrix, text_vector):

        view_transpose = view_matrix.transposed()
        view_transpose.setRow(3, QVector4D())
        view_transpose.setColumn(3, QVector4D(text_vector, 1))
        return view_transpose

    def add_component(self, name, geometry):
        """
        Add a component to the instrument view given a name and its geometry.
        :param name: The name of the component.
        :param geometry: The geometry information of the component that is used to create a mesh.
        """
        entity = Qt3DCore.QEntity(self.component_root_entity)
        mesh = OffMesh(geometry.off_geometry)

        self.add_qcomponents_to_entity(entity, [mesh, self.grey_material])

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

    @staticmethod
    def set_material_properties(material, ambient, diffuse, alpha=None, shininess=None):
        """
        Set the ambient, diffuse, and alpha properties of a material.
        :param material: The material to be modified.
        :param ambient: The desired ambient colour of the material.
        :param diffuse: The desired diffuse colour of the material.
        :param alpha: The desired alpha value of the material. Optional argument as not all material-types have this
                      property.
        :param shininess: The desired shininess of the material. Optional argument as this is only changes for the
                           gnomon cylinders.
        """
        material.setAmbient(ambient)
        material.setDiffuse(diffuse)

        if alpha is not None:
            material.setAlpha(alpha)

        if shininess is not None:
            material.setShininess(shininess)

    def give_colours_to_materials(self):
        """
        Creates several QColours and uses them to configure the different materials that will be used for the objects in
        the 3D view.
        """
        red = QColor("red")
        black = QColor("black")
        grey = QColor("grey")
        blue = QColor("blue")
        green = QColor("darkgreen")
        light_blue = QColor("lightblue")
        dark_red = QColor("#b00")

        self.set_material_properties(self.grey_material, black, grey)
        self.set_material_properties(self.red_material, red, dark_red)
        self.set_material_properties(self.beam_material, blue, light_blue, alpha=0.5)
        self.set_material_properties(self.x_material, red, grey, shininess=0)
        self.set_material_properties(self.y_material, green, green, shininess=0)
        self.set_material_properties(self.z_material, blue, grey, shininess=0)

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
        self.add_qcomponents_to_entity(
            self.cube_entity, [self.cube_mesh, self.red_material]
        )

    @staticmethod
    def add_qcomponents_to_entity(entity, components):
        """
        Takes a QEntity and gives it all of the QComponents that are contained in a list.
        """
        for component in components:
            entity.addComponent(component)

    @staticmethod
    def set_cylinder_mesh_dimensions(cylinder_mesh, radius, length, rings):
        """
        Sets the dimensions of a cylinder mesh.
        :param cylinder_mesh: The cylinder mesh to modify.
        :param radius: The desired radius.
        :param length: The desired length.
        :param rings: The desired number of rings.
        """
        cylinder_mesh.setRadius(radius)
        cylinder_mesh.setLength(length)
        cylinder_mesh.setRings(rings)

    @staticmethod
    def set_beam_transform(cylinder_transform):
        """
        Configures the transform for the beam cylinder by giving it a matrix. The matrix will turn the cylinder sideways
        and then move it "backwards" in the z-direction by 20 units so that it ends at the location of the sample.
        :param cylinder_transform: A QTransform object.
        """
        cylinder_matrix = QMatrix4x4()
        cylinder_matrix.rotate(270, QVector3D(1, 0, 0))
        cylinder_matrix.translate(QVector3D(0, 20, 0))

        cylinder_transform.setMatrix(cylinder_matrix)

    def setup_beam_cylinder(self):
        """
        Sets up the beam cylinder by giving the cylinder entity a mesh, a material, and a transformation.
        """
        self.set_cylinder_mesh_dimensions(
            self.cylinder_mesh, 2.5, self.cylinder_length, 2
        )
        self.set_beam_transform(self.cylinder_transform)
        self.add_qcomponents_to_entity(
            self.cylinder_entity,
            [self.cylinder_mesh, self.beam_material, self.cylinder_transform],
        )

    @staticmethod
    def set_sphere_mesh_radius(sphere_mesh, radius):
        """
        Sets the radius of a sphere mesh.
        :param sphere_mesh: The sphere mesh to modify.
        :param radius: The desired radius.
        """
        sphere_mesh.setRadius(radius)

    @staticmethod
    def set_neutron_animation_properties(
        neutron_animation,
        neutron_animation_controller,
        animation_distance,
        time_span_offset,
    ):
        """
        Prepares a QPropertyAnimation for a neutron by giving it a target, a distance, and loop settings.
        :param neutron_animation: The QPropertyAnimation to be configured.
        :param neutron_animation_controller: The related animation controller object.
        :param animation_distance: The starting distance of the neutron.
        :param time_span_offset: The offset that allows the neutron to move at a different time from other neutrons.
        """
        neutron_animation.setTargetObject(neutron_animation_controller)
        neutron_animation.setPropertyName(b"distance")
        neutron_animation.setStartValue(animation_distance)
        neutron_animation.setEndValue(0)
        neutron_animation.setDuration(500 + time_span_offset)
        neutron_animation.setLoopCount(-1)
        neutron_animation.start()

    def setup_neutrons(self):
        """
        Sets up the neutrons and their animations by preparing their meshes and then giving offset and
        distance parameters to an animation controller.
        """

        # Create lists of x, y, and time offsets for the neutron animations
        x_offsets = [0, 0, 0, 2, -2, 1.4, 1.4, -1.4, -1.4]
        y_offsets = [0, 2, -2, 0, 0, 1.4, -1.4, 1.4, -1.4]
        time_span_offsets = [0, -5, -7, 5, 7, 19, -19, 23, -23]

        neutron_radius = 3

        for i in range(self.num_neutrons):

            self.set_sphere_mesh_radius(
                self.neutron_objects["meshes"][i], neutron_radius
            )

            neutron_animation_controller = NeutronAnimationController(
                x_offsets[i], y_offsets[i], self.neutron_objects["transforms"][i]
            )
            neutron_animation_controller.set_target(
                self.neutron_objects["transforms"][i]
            )

            neutron_animation = QPropertyAnimation(
                self.neutron_objects["transforms"][i]
            )
            self.set_neutron_animation_properties(
                neutron_animation,
                neutron_animation_controller,
                -self.cylinder_length,
                time_span_offsets[i],
            )

            self.neutron_objects["animation_controllers"].append(
                neutron_animation_controller
            )
            self.neutron_objects["animations"].append(neutron_animation)

            self.add_qcomponents_to_entity(
                self.neutron_objects["entities"][i],
                [
                    self.neutron_objects["meshes"][i],
                    self.grey_material,
                    self.neutron_objects["transforms"][i],
                ],
            )

    def initialise_view(self):
        """
        Calls the methods for defining materials, setting up the sample cube, and setting up the neutrons. Beam-related
        functions are called outside of this method to ensure that those things are generated last.
        """
        self.give_colours_to_materials()
        self.setup_sample_cube()
        self.setup_neutrons()
        self.create_gnomon()
