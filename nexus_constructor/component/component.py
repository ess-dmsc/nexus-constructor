import h5py
from typing import Any, List, Optional, Union, Tuple
from PySide2.QtGui import QVector3D
from nexus_constructor.nexus import nexus_wrapper as nx
from nexus_constructor.nexus.nexus_wrapper import get_nx_class
from nexus_constructor.pixel_data import PixelMapping, PixelGrid, PixelData
from nexus_constructor.pixel_data_to_nexus_utils import (
    get_x_offsets_from_pixel_grid,
    get_y_offsets_from_pixel_grid,
    get_z_offsets_from_pixel_grid,
    get_detector_ids_from_pixel_grid,
    get_detector_number_from_pixel_mapping,
)
from nexus_constructor.transformations import Transformation, TransformationsList
from nexus_constructor.ui_utils import qvector3d_to_numpy_array, generate_unique_name
from nexus_constructor.geometry.cylindrical_geometry import (
    CylindricalGeometry,
    calculate_vertices,
)
from nexus_constructor.geometry import (
    OFFGeometryNexus,
    OFFGeometry,
    record_faces_in_file,
    record_vertices_in_file,
)
from nexus_constructor.geometry.utils import validate_nonzero_qvector
import numpy as np

SHAPE_GROUP_NAME = "shape"
PIXEL_SHAPE_GROUP_NAME = "pixel_shape"
CYLINDRICAL_GEOMETRY_NEXUS_NAME = "NXcylindrical_geometry"
OFF_GEOMETRY_NEXUS_NAME = "NXoff_geometry"
DEPENDS_ON_STR = "depends_on"


class DependencyError(Exception):
    """
    Raised when trying to carry out an operation which would invalidate the depends_on chain
    """

    pass


def _normalise(input_vector: QVector3D):
    """
    Normalise to unit vector

    :param input_vector: Input vector
    :return: Unit vector, magnitude
    """
    magnitude = input_vector.length()
    if magnitude == 0:
        return QVector3D(0.0, 0.0, 0.0), 0.0

    return input_vector.normalized(), magnitude


def _generate_incremental_name(base_name, group: h5py.Group):
    number = 1
    while f"{base_name}_{number}" in group:
        number += 1
    return f"{base_name}_{number}"


def _transforms_are_equivalent(
    transform_1: Transformation, transform_2: Transformation
):
    return transform_1.absolute_path == transform_2.absolute_path


def get_shape_from_component(
    component_group: h5py.Group, nexus_file: nx.NexusWrapper, shape_group_name: str
):
    if shape_group_name in component_group:
        shape_group = component_group[shape_group_name]
        nx_class = get_nx_class(shape_group)
        if nx_class == CYLINDRICAL_GEOMETRY_NEXUS_NAME:
            return CylindricalGeometry(nexus_file, shape_group)
        if nx_class == OFF_GEOMETRY_NEXUS_NAME:
            return OFFGeometryNexus(nexus_file, shape_group)


class Component:
    """
    Provides an interface to an existing component group in a NeXus file
    """

    def __init__(self, nexus_file: nx.NexusWrapper, group: h5py.Group):
        self.file = nexus_file
        self.group = group

    @property
    def name(self):
        return nx.get_name_of_node(self.group)

    @name.setter
    def name(self, new_name: str):
        self.file.rename_node(self.group, new_name)

    @property
    def absolute_path(self):
        """
        Get absolute path of the component group in the NeXus file,
        this is guaranteed to be unique so it can be used as an ID for this Component
        :return: absolute path of the transform dataset in the NeXus file,
        """
        return self.group.name

    def get_field(self, name: str):
        return self.file.get_field_value(self.group, name)

    def set_field(self, name: str, value: Any, dtype=None):
        self.file.set_field_value(self.group, name, value, dtype)

    @property
    def nx_class(self):
        return get_nx_class(self.group)

    @nx_class.setter
    def nx_class(self, nx_class: str):
        self.file.set_nx_class(self.group, nx_class)

    @property
    def description(self):
        return self.file.get_field_value(self.group, "description")

    @description.setter
    def description(self, description: str):
        if description:
            self.file.set_field_value(self.group, "description", description, str)

    @property
    def transforms_full_chain(self) -> TransformationsList:
        """
        Gets all transforms in the depends_on chain for this component
        :return: List of transforms
        """
        transforms = TransformationsList(self)
        depends_on = self.get_field(DEPENDS_ON_STR)
        self._get_transform(depends_on, transforms)
        return transforms

    def _get_transform(
        self,
        depends_on: str,
        transforms: List[Transformation],
        local_only: bool = False,
    ):
        """
        Recursive function, appends each transform in depends_on chain to transforms list
        :param depends_on: The next depends_on string to find the next transformation in the chain
        :param transforms: The list to populate with transformations
        :param local_only: If True then only add transformations which are stored within this component
        """
        if depends_on is not None and depends_on != ".":
            transform_dataset = self.file.nexus_file[depends_on]
            if (
                local_only
                and transform_dataset.parent.parent.name != self.absolute_path
            ):
                # We're done, the next transformation is not stored in this component
                return
            transforms.append(Transformation(self.file, transform_dataset))
            if DEPENDS_ON_STR in transform_dataset.attrs.keys():
                self._get_transform(transform_dataset.attrs[DEPENDS_ON_STR], transforms)

    @property
    def transforms(self) -> TransformationsList:
        """
        Gets transforms in the depends_on chain but only those which are local to
        this component's group in the NeXus file
        :return:
        """
        transforms = TransformationsList(self)
        depends_on = self.get_field(DEPENDS_ON_STR)
        self._get_transform(depends_on, transforms, local_only=True)
        return transforms

    def add_translation(
        self, vector: QVector3D, name: str = None, depends_on: Transformation = None
    ) -> Transformation:
        """
        Note, currently assumes translation is in metres
        :param vector: direction and magnitude of translation as a 3D vector
        :param name: name of the translation group (Optional)
        :param depends_on: existing transformation which the new one depends on (otherwise relative to origin)
        """
        transforms_group = self.file.create_transformations_group_if_does_not_exist(
            self.group
        )
        if name is None:
            name = _generate_incremental_name("translation", transforms_group)
        unit_vector, magnitude = _normalise(vector)
        field = self.file.set_field_value(transforms_group, name, magnitude, float)
        self.file.set_attribute_value(field, "units", "m")
        self.file.set_attribute_value(
            field, "vector", qvector3d_to_numpy_array(unit_vector)
        )
        self.file.set_attribute_value(field, "transformation_type", "Translation")

        translation_transform = Transformation(self.file, field)
        translation_transform.depends_on = depends_on
        return translation_transform

    def add_rotation(
        self,
        axis: QVector3D,
        angle: float,
        name: str = None,
        depends_on: Transformation = None,
    ) -> Transformation:
        """
        Note, currently assumes angle is in degrees
        :param axis: axis
        :param angle:
        :param name: Name of the rotation group (Optional)
        :param depends_on: existing transformation which the new one depends on (otherwise relative to origin)
        """
        transforms_group = self.file.create_transformations_group_if_does_not_exist(
            self.group
        )
        if name is None:
            name = _generate_incremental_name("rotation", transforms_group)
        field = self.file.set_field_value(transforms_group, name, angle, float)
        self.file.set_attribute_value(field, "units", "degrees")
        self.file.set_attribute_value(field, "vector", qvector3d_to_numpy_array(axis))
        self.file.set_attribute_value(field, "transformation_type", "Rotation")
        rotation_transform = Transformation(self.file, field)
        rotation_transform.depends_on = depends_on
        return rotation_transform

    def _transform_is_in_this_component(self, transform: Transformation) -> bool:
        return transform.dataset.parent.parent.name == self.absolute_path

    def remove_transformation(self, transform: Transformation):
        if not self._transform_is_in_this_component(transform):
            raise PermissionError(
                "Transform is not in this component, do not have permission to delete"
            )

        dependents = transform.get_dependents()
        if dependents:
            raise DependencyError(
                f"Cannot delete transformation, it is a dependency of {dependents}"
            )

        # Remove whole transformations group if this is the only transformation in it
        if len(transform.dataset.parent.keys()) == 1:
            self.file.delete_node(transform.dataset.parent)
        # Otherwise just remove the transformation from the group
        else:
            self.file.delete_node(transform.dataset)

    @property
    def depends_on(self):
        depends_on_path = self.file.get_field_value(self.group, DEPENDS_ON_STR)
        if depends_on_path is None:
            return None
        return Transformation(self.file, self.file.nexus_file[depends_on_path])

    @depends_on.setter
    def depends_on(self, transformation: Transformation):
        existing_depends_on = self.file.get_attribute_value(self.group, DEPENDS_ON_STR)
        if existing_depends_on is not None:
            Transformation(
                self.file, self.file[existing_depends_on]
            ).deregister_dependent(self)

        if transformation is None:
            self.file.set_field_value(self.group, DEPENDS_ON_STR, ".", str)
        else:
            self.file.set_field_value(
                self.group, DEPENDS_ON_STR, transformation.absolute_path, str
            )
            transformation.register_dependent(self)

    def set_cylinder_shape(
        self,
        axis_direction: QVector3D = QVector3D(0.0, 0.0, 1.0),
        height: float = 1.0,
        radius: float = 1.0,
        units: Union[str, bytes] = "m",
        pixel_data: PixelData = None,
    ) -> CylindricalGeometry:
        """
        Sets the shape of the component to be a cylinder
        Overrides any existing shape
        """
        self.remove_shape()
        validate_nonzero_qvector(axis_direction)

        shape_group = self.create_shape_nx_group(
            CYLINDRICAL_GEOMETRY_NEXUS_NAME, type(pixel_data) is PixelGrid
        )

        pixel_mapping = None
        if type(pixel_data) is PixelMapping:
            pixel_mapping = pixel_data

        vertices = calculate_vertices(axis_direction, height, radius)
        vertices_field = self.file.set_field_value(shape_group, "vertices", vertices)
        # Specify 0th vertex is base centre, 1st is base edge, 2nd is top centre
        self.file.set_field_value(shape_group, "cylinders", np.array([0, 1, 2]))
        self.file.set_attribute_value(vertices_field, "units", units)
        return CylindricalGeometry(self.file, shape_group, pixel_mapping)

    def set_off_shape(
        self,
        loaded_geometry: OFFGeometry,
        units: str = "",
        filename: str = "",
        pixel_data: PixelData = None,
    ) -> OFFGeometryNexus:
        """
        Sets the shape of the component to be a mesh
        Overrides any existing shape
        """
        self.remove_shape()

        shape_group = self.create_shape_nx_group(
            OFF_GEOMETRY_NEXUS_NAME, type(pixel_data) is PixelGrid
        )

        pixel_mapping = None
        if type(pixel_data) is PixelMapping:
            pixel_mapping = pixel_data

        record_faces_in_file(self.file, shape_group, loaded_geometry.faces)
        record_vertices_in_file(self.file, shape_group, loaded_geometry.vertices)
        return OFFGeometryNexus(self.file, shape_group, units, filename, pixel_mapping)

    def create_shape_nx_group(
        self, nexus_name: str, shape_is_single_pixel: bool = False
    ):
        """
        Creates an NXGroup for the shape information. If the shape is a Pixel Grid/Single Pixel then this is stored
        with the name `pixel_shape`, otherwise it is stored as `shape`.
        :param nexus_name: The Nexus name for the shape. This will either be (NXcylindrical/NXoff)_geometry
        :param shape_is_single_pixel: Whether or not the shape is a single pixel.
        :return: The shape group.
        """

        if shape_is_single_pixel:
            shape_group = self.file.create_nx_group(
                PIXEL_SHAPE_GROUP_NAME, nexus_name, self.group
            )
        else:
            shape_group = self.file.create_nx_group(
                SHAPE_GROUP_NAME, nexus_name, self.group
            )
        return shape_group

    def get_shape(
        self
    ) -> Tuple[
        Optional[Union[OFFGeometry, CylindricalGeometry]],
        Optional[List[Transformation]],
    ]:
        """
        Get the shape of the component if there is one defined, and optionally a
        list of transformations relative to the component's depends_on chain which
        describe where the shape should be repeated
        (used in subclass for components where the shape describes each pixel)

        :return: Component shape, each transformation where the shape is repeated
        """
        shape = get_shape_from_component(self.group, self.file, SHAPE_GROUP_NAME)
        return shape, None

    def remove_shape(self):
        if SHAPE_GROUP_NAME in self.group:
            del self.group[SHAPE_GROUP_NAME]

    def duplicate(self, components_list: List["Component"]) -> "Component":
        return Component(
            self.file,
            self.file.duplicate_nx_group(
                self.group, generate_unique_name(self.name, components_list)
            ),
        )

    def record_pixel_grid(self, pixel_grid: PixelGrid):
        """
        Records the pixel grid data to the NeXus file.
        :param pixel_grid: The PixelGrid created from the input provided to the Add/Edit Component Window.
        """
        self.set_field(
            "x_pixel_offset", get_x_offsets_from_pixel_grid(pixel_grid), "float64"
        )
        self.set_field(
            "y_pixel_offset", get_y_offsets_from_pixel_grid(pixel_grid), "float64"
        )
        self.set_field(
            "z_pixel_offset", get_z_offsets_from_pixel_grid(pixel_grid), "float64"
        )
        self.set_field(
            "detector_number", get_detector_ids_from_pixel_grid(pixel_grid), "int64"
        )

    def record_detector_number(self, pixel_mapping: PixelMapping):

        self.set_field(
            "detector_number",
            get_detector_number_from_pixel_mapping(pixel_mapping),
            "int64",
        )
