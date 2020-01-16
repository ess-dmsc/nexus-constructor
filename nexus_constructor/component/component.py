import h5py
from typing import Any, List, Optional, Union, Tuple
from PySide2.QtGui import QVector3D, QMatrix4x4
from PySide2.Qt3DCore import Qt3DCore

from nexus_constructor.component.pixel_shape import PixelShape
from nexus_constructor.component.transformations_list import TransformationsList
from nexus_constructor.nexus import nexus_wrapper as nx
from nexus_constructor.nexus.nexus_wrapper import get_nx_class, get_fields
from nexus_constructor.pixel_data import PixelMapping, PixelGrid, PixelData
from nexus_constructor.pixel_data_to_nexus_utils import (
    get_x_offsets_from_pixel_grid,
    get_y_offsets_from_pixel_grid,
    get_z_offsets_from_pixel_grid,
    get_detector_ids_from_pixel_grid,
    get_detector_number_from_pixel_mapping,
    PIXEL_FIELDS,
)
from nexus_constructor.transformation_types import TransformationType
from nexus_constructor.transformations import Transformation
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
from nexus_constructor.component.component_shape import (
    CYLINDRICAL_GEOMETRY_NEXUS_NAME,
    OFF_GEOMETRY_NEXUS_NAME,
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
    ComponentShape,
)
import numpy as np

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


class Component:
    """
    Provides an interface to an existing component group in a NeXus file
    """

    def __init__(
        self,
        nexus_file: nx.NexusWrapper,
        group: h5py.Group,
        shape: Optional[ComponentShape] = None,
    ):
        self.file = nexus_file
        self.group = group
        if shape is not None:
            self._shape = shape
        else:
            self._shape = ComponentShape(nexus_file, group)

    def __eq__(self, other):
        try:
            return other.absolute_path == self.absolute_path
        except Exception:
            return False

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

    def delete_field(self, name: str):
        self.file.delete_field_value(self.group, name)

    def get_fields(self):
        return get_fields(self.group)

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
            new_transform = Transformation(self.file, transform_dataset)
            new_transform.parent = transforms
            transforms.append(new_transform)
            if DEPENDS_ON_STR in transform_dataset.attrs.keys():
                self._get_transform(
                    self.file.get_attribute_value(transform_dataset, DEPENDS_ON_STR),
                    transforms,
                    local_only,
                )

    @property
    def transform(self) -> Qt3DCore.QTransform:
        """
        Get a QTransform describing the position and orientation of the component
        """
        transform_matrix = QMatrix4x4()
        for transform in self.transforms_full_chain:
            transform_matrix *= transform.qmatrix
        transformation = Qt3DCore.QTransform()
        transformation.setMatrix(transform_matrix)
        return transformation

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
            name = _generate_incremental_name(
                TransformationType.TRANSLATION.value, transforms_group
            )
        unit_vector, magnitude = _normalise(vector)
        field = self.file.set_field_value(transforms_group, name, magnitude, float)
        self.file.set_attribute_value(field, "units", "m")
        self.file.set_attribute_value(
            field, "vector", qvector3d_to_numpy_array(unit_vector)
        )
        self.file.set_attribute_value(
            field, "transformation_type", TransformationType.TRANSLATION.value
        )

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
            name = _generate_incremental_name(
                TransformationType.ROTATION.value, transforms_group
            )
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
        if isinstance(pixel_data, PixelMapping):
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
            OFF_GEOMETRY_NEXUS_NAME, isinstance(pixel_data, PixelGrid)
        )

        pixel_mapping = None
        if isinstance(pixel_data, PixelMapping):
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
            self._shape = PixelShape(self.file, self.group)
        else:
            shape_group = self.file.create_nx_group(
                SHAPE_GROUP_NAME, nexus_name, self.group
            )
            self._shape = ComponentShape(self.file, self.group)
        return shape_group

    @property
    def shape(
        self
    ) -> Tuple[
        Optional[Union[OFFGeometry, CylindricalGeometry]], Optional[List[QVector3D]]
    ]:
        """
        Get the shape of the component if there is one defined, and optionally a
        list of transformations relative to the component's depends_on chain which
        describe where the shape should be repeated
        (used in subclass for components where the shape describes each pixel)

        :return: Component shape, each transformation where the shape is repeated
        """
        return self._shape.get_shape()

    def remove_shape(self):
        self._shape.remove_shape()

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

    def record_pixel_mapping(self, pixel_mapping: PixelMapping):
        """
        Records the pixel mapping data to the NeXus file.
        :param pixel_mapping: The PixelMapping created from the input provided to the Add/Edit Component Window.
        """
        self.set_field(
            "detector_number",
            get_detector_number_from_pixel_mapping(pixel_mapping),
            "int64",
        )

    def clear_pixel_data(self):
        """
        Removes the existing pixel data from the NeXus file. Used when editing pixel data.
        """
        for field in PIXEL_FIELDS:
            self.delete_field(field)
