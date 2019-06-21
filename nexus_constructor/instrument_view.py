from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtCore import QPropertyAnimation
from PySide2.QtGui import QVector3D, QColor, QMatrix4x4
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

        # Initialise materials
        self.grey_material = Qt3DExtras.QPhongMaterial()
        self.red_material = Qt3DExtras.QPhongMaterial()
        self.beam_material = Qt3DExtras.QPhongAlphaMaterial()
        self.green_material = Qt3DExtras.QPhongMaterial()

        # Initialise cube objects
        self.sample_cube_dimensions = [1, 1, 1]
        self.cube_entity = Qt3DCore.QEntity(self.root_entity)
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
            self.neutron_objects["entities"].append(Qt3DCore.QEntity(self.root_entity))
            self.neutron_objects["meshes"].append(Qt3DExtras.QSphereMesh())
            self.neutron_objects["transforms"].append(Qt3DCore.QTransform())

        self.cylinder_length = 40

        self.initialise_view()

        # Initialise beam objects
        self.cylinder_entity = Qt3DCore.QEntity(self.root_entity)
        self.cylinder_mesh = Qt3DExtras.QCylinderMesh()
        self.cylinder_transform = Qt3DCore.QTransform()

        # Dictionaries for component-related objects also to prevent them from going out of scope
        self.component_meshes = {}
        self.component_entities = {}
        self.component_transformations = {}

        # Insert the beam cylinder last. This ensures that the semi-transparency works correctly.
        self.setup_beam_cylinder()

    def add_component(self, name, geometry):
        """
        Add a component to the instrument view given a name and its geometry.
        :param name: The name of the component.
        :param geometry: The geometry information of the component that is used to create a mesh.
        """
        entity = Qt3DCore.QEntity(self.root_entity)
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

        self.set_material_properties(self.grey_material, black, grey)
        self.set_material_properties(self.red_material, red, dark_red)
        self.set_material_properties(self.green_material, grey, grey)
        self.set_material_properties(self.beam_material, blue, light_blue, 0.5)

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
