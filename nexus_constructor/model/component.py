import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

import attr
import numpy as np
from PySide6.Qt3DCore import Qt3DCore
from PySide6.QtGui import QMatrix4x4, QTransform, QVector3D

from nexus_constructor.common_attrs import (
    CYLINDRICAL_GEOMETRY_NX_CLASS,
    GEOMETRY_GROUP_NAME,
    NX_TRANSFORMATIONS,
    OFF_GEOMETRY_NX_CLASS,
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
    CommonAttrs,
    CommonKeys,
    NodeType,
    TransformationType,
)
from nexus_constructor.geometry.pixel_data import PixelData, PixelGrid, PixelMapping
from nexus_constructor.geometry.pixel_data_utils import (
    PIXEL_FIELDS,
    get_detector_faces_from_pixel_mapping,
    get_detector_ids_from_pixel_grid,
    get_detector_number_from_pixel_mapping,
    get_x_offsets_from_pixel_grid,
    get_y_offsets_from_pixel_grid,
    get_z_offsets_from_pixel_grid,
)
from nexus_constructor.geometry.utils import validate_nonzero_qvector
from nexus_constructor.model.geometry import (
    CYLINDERS,
    DETECTOR_NUMBER,
    X_PIXEL_OFFSET,
    Y_PIXEL_OFFSET,
    Z_PIXEL_OFFSET,
    BoxGeometry,
    CylindricalGeometry,
    NoShapeGeometry,
    OFFGeometry,
    OFFGeometryNexus,
)
from nexus_constructor.model.group import TRANSFORMS_GROUP_NAME, Group
from nexus_constructor.model.helpers import _generate_incremental_name
from nexus_constructor.model.module import DATASET, Dataset, StreamModule
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.model.value_type import ValueTypes
from nexus_constructor.transformations_list import TransformationsList
from nexus_constructor.unit_utils import METRES, calculate_unit_conversion_factor

if TYPE_CHECKING:
    from nexus_constructor.component_tree_model import ComponentInfo  # noqa: F401


def _normalise(input_vector: QVector3D) -> Tuple[QVector3D, float]:
    """
    Normalise to unit vector

    :param input_vector: Input vector
    :return: Unit vector, magnitude
    """
    magnitude = input_vector.length()
    if magnitude == 0:
        return QVector3D(0.0, 0.0, 0.0), 0.0

    return input_vector.normalized(), magnitude


def _get_shape_group_for_pixel_data(pixel_data: PixelData) -> str:
    """
    Determines which group the geometry should be placed in based on the type of PixelData.
    :param pixel_data: The pixel data. Can either be grid or mapping.
    :return: The name of the key for shape group.
    """
    if isinstance(pixel_data, PixelGrid):
        return PIXEL_SHAPE_GROUP_NAME
    return SHAPE_GROUP_NAME


@attr.s
class Component(Group):
    """
    Base class for a component object. In the NeXus file this would translate to the component group.
    """

    _depends_on: Transformation = attr.ib(default=None)
    has_link: bool = attr.ib(default=None)
    component_info: Optional["ComponentInfo"] = None
    stored_transforms: Optional[list] = None
    name: str = ""
    parent_node: Optional[Group] = None

    @property
    def stored_items(self) -> List:
        if not self.stored_transforms:
            return self.children
        return self.stored_transforms + self.children

    @property
    def depends_on(self) -> "Transformation":
        return self._depends_on

    @depends_on.setter
    def depends_on(self, new_depends_on: "Transformation"):
        if self.depends_on is not None:
            # deregister this component as a dependent of the old depends_on transformation
            self.depends_on.deregister_dependent(self)

        self._depends_on = new_depends_on
        try:
            self[CommonAttrs.DEPENDS_ON] = Dataset(
                parent_node=self,
                name=CommonAttrs.DEPENDS_ON,
                values=self._depends_on.absolute_path,
            )
        except AttributeError:
            logging.debug(
                f"NeXus Constructor cannot display depends_on for {self.name} in tree structure."
            )
        if new_depends_on is not None:
            new_depends_on.register_dependent(self)

    @property
    def qtransform(self) -> QTransform:
        """
        Creates a QTransform based on the full chain of transforms this component points to.
        Where T_1 depends on T_2 which depends on T_3:
        the final transformation T_f = T_3*T_2*T_1

        :return: QTransform of final transformation
        """
        transform_matrix = QMatrix4x4()  # Identity matrix
        for transform in self.transforms_full_chain:
            # Left multiply each new matrix
            transform_matrix = transform.qmatrix * transform_matrix
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
        try:
            self._get_depends_on(
                self,
                transforms,
                local_only=True,
            )
        except AttributeError:
            pass
        return transforms

    def _get_depends_on(
        self,
        current_item: Union[Transformation, "Component"],
        transforms: List[Transformation],
        local_only: bool = False,
    ):
        """
        Recursive function, appends each transform in depends_on chain to transforms list
        :param current_item: the current transformation, used to get the next depends_on
        :param transforms: The list to populate with transformations
        :param local_only: If True then only add transformations which are stored within this component
        """
        depends_on_transform = current_item.depends_on
        if isinstance(depends_on_transform, Component):
            depends_on_transform = depends_on_transform.depends_on
        if depends_on_transform is not None:
            if local_only and depends_on_transform.parent_component != self:
                # reached an external transform - ignore if local_only
                return
            if depends_on_transform.depends_on == depends_on_transform:
                # reached the end of the chain
                return

            transforms.append(depends_on_transform)
            self._get_depends_on(depends_on_transform, transforms, local_only)

    @property
    def transforms_full_chain(self) -> TransformationsList:
        """
        Gets all transforms in the depends_on chain for this component
        :return: List of transforms
        """
        transforms = TransformationsList(self)
        try:
            self._get_depends_on(
                self,
                transforms,
                local_only=False,
            )
        except AttributeError:
            pass
        return transforms

    def add_translation(
        self,
        vector: QVector3D,
        name: str = None,
        depends_on: Transformation = None,
        values: Dataset = Dataset(
            parent_node=None, name="", values=0, type=ValueTypes.DOUBLE
        ),
        target_pos: int = -1,
    ) -> Transformation:
        """
        Note, currently assumes translation is in metres
        :param vector: direction and magnitude of translation as a 3D vector
        :param name: name of the translation group (Optional)
        :param depends_on: existing transformation which the new one depends on (otherwise relative to origin)
        :param values: The translation distance information.
        :param target_pos: Target position.
        """
        values.parent_node = self
        unit_vector, _ = _normalise(vector)
        return self._create_and_add_transform(
            name,
            TransformationType.TRANSLATION,
            0.0,
            "m",
            unit_vector,
            depends_on,
            values,
            target_pos,
        )

    def add_rotation(
        self,
        axis: QVector3D,
        angle: float,
        name: str = None,
        depends_on: Transformation = None,
        values: Dataset = Dataset(
            parent_node=None,
            name="",
            values=0,
            type=ValueTypes.DOUBLE,
        ),
        target_pos: int = -1,
    ) -> Transformation:
        """
        Note, currently assumes angle is in degrees
        :param axis: axis
        :param angle:
        :param name: Name of the rotation group (Optional)
        :param depends_on: existing transformation which the new one depends on (otherwise relative to origin)
        :param values: The translation distance information.
        :param target_pos: Target position.
        """
        values.parent_node = self
        return self._create_and_add_transform(
            name,
            TransformationType.ROTATION,
            angle,
            "degrees",
            axis,
            depends_on,
            values,
            target_pos,
        )

    def _create_and_add_transform(
        self,
        name: str,
        transformation_type: str,
        angle_or_magnitude: float,
        units: str,
        vector: QVector3D,
        depends_on: Transformation,
        values: Union[Dataset, Group, StreamModule],
        target_pos: int = -1,
    ) -> Transformation:
        if name is None:
            name = _generate_incremental_name(transformation_type, self.transforms)

        type = ValueTypes.DOUBLE
        if isinstance(values, Dataset):
            type = values.type
        elif isinstance(values, StreamModule):
            try:
                type = "double"  # type: ignore
            except AttributeError:
                pass
        transform = Transformation(
            name=name,
            parent_node=self.get_transforms_group(),
            type=type,
            values=values,
        )
        transform.transform_type = transformation_type
        transform.ui_value = angle_or_magnitude
        transform.units = units
        transform.vector = vector
        transform.depends_on = depends_on
        transform.parent_component = self
        if target_pos:
            self.get_transforms_group().children.insert(target_pos, transform)  # type: ignore
        else:
            self.get_transforms_group()[name] = transform  # type: ignore

        return transform

    def remove_transformation(self, transform: Transformation):
        # Check the transform has no dependents, excluding this component
        if (
            transform.dependents
            and not len(transform.dependents) == 1
            and not transform.dependents[0] == self
        ):
            raise Exception
        del self.get_transforms_group()[transform.name]
        transform.remove_from_dependee_chain()

    def get_transforms_group(self) -> Group:
        if self[TRANSFORMS_GROUP_NAME] is not None:
            return self[TRANSFORMS_GROUP_NAME]

        self[TRANSFORMS_GROUP_NAME] = Group(TRANSFORMS_GROUP_NAME, parent_node=self)
        self[TRANSFORMS_GROUP_NAME].nx_class = "NXtransformations"
        return self[TRANSFORMS_GROUP_NAME]

    @property
    def shape(
        self,
    ) -> Tuple[
        Union[NoShapeGeometry, BoxGeometry, CylindricalGeometry, OFFGeometryNexus],
        Optional[List[QVector3D]],
    ]:
        if PIXEL_SHAPE_GROUP_NAME in self:
            return (
                self[PIXEL_SHAPE_GROUP_NAME],
                self._create_transformation_vectors_for_pixel_offsets(),
            )
        if SHAPE_GROUP_NAME in self:
            return self[SHAPE_GROUP_NAME], None
        if GEOMETRY_GROUP_NAME in self:
            return (
                self[GEOMETRY_GROUP_NAME],
                self._create_transformation_vectors_for_pixel_offsets(),
            )
        return NoShapeGeometry(), None

    def remove_shape(self):
        for group_name in [
            GEOMETRY_GROUP_NAME,
            PIXEL_SHAPE_GROUP_NAME,
            SHAPE_GROUP_NAME,
        ]:
            if group_name in self:
                del self[group_name]

    def set_off_shape(
        self,
        loaded_geometry: OFFGeometry,
        units: str = "",
        filename: str = "",
        pixel_data=None,
    ) -> OFFGeometryNexus:
        self.remove_shape()

        shape_group = _get_shape_group_for_pixel_data(pixel_data)
        geometry = OFFGeometryNexus(shape_group)
        geometry.nx_class = OFF_GEOMETRY_NX_CLASS
        geometry.record_faces(loaded_geometry.faces)
        geometry.record_vertices(loaded_geometry.vertices)
        geometry.colors = loaded_geometry.colors
        geometry.units = units
        geometry.file_path = filename

        if isinstance(pixel_data, PixelMapping):
            geometry.detector_faces = get_detector_faces_from_pixel_mapping(pixel_data)

        self[shape_group] = geometry
        return geometry

    def set_box_shape(
        self,
        length: float = 1.0,
        width: float = 1.0,
        height: float = 1.0,
        units: str = "m",
        pixel_data=None,
    ) -> BoxGeometry:
        self.remove_shape()
        geometry = BoxGeometry(length, width, height, GEOMETRY_GROUP_NAME, units)
        if isinstance(pixel_data, PixelMapping):
            geometry.detector_number = get_detector_number_from_pixel_mapping(
                pixel_data
            )
        self[GEOMETRY_GROUP_NAME] = geometry
        return geometry

    def set_cylinder_shape(
        self,
        axis_direction: QVector3D = QVector3D(0.0, 0.0, 1.0),
        height: float = 1.0,
        radius: float = 1.0,
        units: Union[str, bytes] = "m",
        pixel_data=None,
    ) -> Optional[CylindricalGeometry]:
        if validate_nonzero_qvector(axis_direction):
            return None
        self.remove_shape()
        shape_group = _get_shape_group_for_pixel_data(pixel_data)
        geometry = CylindricalGeometry(shape_group)
        geometry.nx_class = CYLINDRICAL_GEOMETRY_NX_CLASS

        vertices = CylindricalGeometry.calculate_vertices(
            axis_direction, height, radius
        )
        geometry.set_field_value(CommonAttrs.VERTICES, vertices, ValueTypes.FLOAT)

        # # Specify 0th vertex is base centre, 1st is base edge, 2nd is top centre
        geometry.set_field_value(CYLINDERS, np.array([0, 1, 2]), ValueTypes.INT)
        geometry[CommonAttrs.VERTICES].attributes.set_attribute_value(
            CommonAttrs.UNITS, units
        )

        if isinstance(pixel_data, PixelMapping):
            geometry.detector_number = get_detector_number_from_pixel_mapping(
                pixel_data
            )
        self[shape_group] = geometry
        return geometry

    def clear_pixel_data(self):
        for field_name in PIXEL_FIELDS:
            try:
                del self[field_name]
            except AttributeError:
                pass

    def has_pixel_shape(self):
        return PIXEL_SHAPE_GROUP_NAME in self

    def record_pixel_grid(self, pixel_grid: PixelGrid, unit: str = ""):
        """
        Records the pixel grid data to the NeXus file.
        :param pixel_grid: The PixelGrid created from the input provided to the Add/Edit Component Window.
        :param unit: length unit used in offset.
        """
        self.set_field_value(
            X_PIXEL_OFFSET,
            get_x_offsets_from_pixel_grid(pixel_grid),
            ValueTypes.FLOAT,
            unit,
        )
        self.set_field_value(
            Y_PIXEL_OFFSET,
            get_y_offsets_from_pixel_grid(pixel_grid),
            ValueTypes.FLOAT,
            unit,
        )
        self.set_field_value(
            Z_PIXEL_OFFSET,
            get_z_offsets_from_pixel_grid(pixel_grid),
            ValueTypes.FLOAT,
            unit,
        )
        self.set_field_value(
            DETECTOR_NUMBER,
            np.array(get_detector_ids_from_pixel_grid(pixel_grid)),
            ValueTypes.INT,
        )
        if pixel_grid.gap_every_rows and pixel_grid.row_gap_height:
            self.attributes.set_attribute_value(
                "pixelgrid_gap_every_rows", pixel_grid.gap_every_rows
            )
            self.attributes.set_attribute_value(
                "pixelgrid_row_gap_height", pixel_grid.row_gap_height
            )
        if pixel_grid.gap_every_columns and pixel_grid.column_gap_width:
            self.attributes.set_attribute_value(
                "pixelgrid_gap_every_columns", pixel_grid.gap_every_columns
            )
            self.attributes.set_attribute_value(
                "pixelgrid_column_gap_width", pixel_grid.column_gap_width
            )

    def record_pixel_mapping(self, pixel_mapping: PixelMapping):
        """
        Records the pixel mapping data to the NeXus file.
        :param pixel_mapping: The PixelMapping created from the input provided to the Add/Edit Component Window.
        """
        self.set_field_value(
            DETECTOR_NUMBER,
            np.array(get_detector_number_from_pixel_mapping(pixel_mapping)),
            ValueTypes.INT,
        )

    def __flatten_list(self, list_to_flat):
        flat_list = []
        if list_to_flat and not isinstance(list_to_flat[0], list):
            return list_to_flat
        for sublist in list_to_flat:
            flat_list += sublist
        return flat_list

    def _create_transformation_vectors_for_pixel_offsets(
        self,
    ) -> Optional[List[QVector3D]]:
        """
        Construct a transformation (as a QVector3D) for each pixel offset
        """
        try:
            units = self.get_field_attribute(X_PIXEL_OFFSET, CommonAttrs.UNITS)
            unit_conversion_factor = calculate_unit_conversion_factor(units, METRES)
            x_offsets = (
                np.array(self.get_field_value(X_PIXEL_OFFSET)) * unit_conversion_factor
            )
            y_offsets = (
                np.array(self.get_field_value(Y_PIXEL_OFFSET)) * unit_conversion_factor
            )
            x_offsets = x_offsets.tolist()
            y_offsets = y_offsets.tolist()
        except AttributeError:
            logging.info(
                "In pixel_shape_component expected to find x_pixel_offset and y_pixel_offset datasets"
            )
            return None
        try:
            z_offsets = self.get_field_value(Z_PIXEL_OFFSET)
        except AttributeError:
            z_offsets = np.zeros_like(x_offsets)
        if not isinstance(x_offsets, list):
            x_offsets = x_offsets.flatten()
        else:
            x_offsets = self.__flatten_list(x_offsets)
        if not isinstance(y_offsets, list):
            y_offsets = y_offsets.flatten()
        else:
            y_offsets = self.__flatten_list(y_offsets)
        if not isinstance(z_offsets, list):
            z_offsets = z_offsets.flatten()
        else:
            z_offsets = self.__flatten_list(z_offsets)
        # offsets datasets can be 2D to match dimensionality of detector, so flatten to 1D
        return [QVector3D(x, y, z) for x, y, z in zip(x_offsets, y_offsets, z_offsets)]

    def as_dict(self, error_collector: List[str]) -> Dict[str, Any]:
        dictionary = super(Component, self).as_dict(error_collector)
        if self.transforms:
            # Add transformations in a child group
            dictionary[CommonKeys.CHILDREN].append(
                {
                    CommonKeys.TYPE: NodeType.GROUP,
                    CommonKeys.NAME: TRANSFORMS_GROUP_NAME,
                    CommonKeys.CHILDREN: [
                        transform.as_dict(error_collector)
                        for transform in self.transforms
                    ],
                    CommonKeys.ATTRIBUTES: [
                        {
                            CommonKeys.NAME: CommonAttrs.NX_CLASS,
                            CommonKeys.VALUES: NX_TRANSFORMATIONS,
                        }
                    ],
                }
            )
        try:
            if self.depends_on is not None and CommonAttrs.DEPENDS_ON not in self:
                dictionary[CommonKeys.CHILDREN].append(
                    {
                        CommonKeys.MODULE: DATASET,
                        NodeType.CONFIG: {
                            CommonKeys.NAME: CommonAttrs.DEPENDS_ON,
                            CommonKeys.DATA_TYPE: ValueTypes.STRING,
                            CommonKeys.VALUES: self.depends_on.absolute_path,
                        },
                    }
                )
        except AttributeError:
            pass
        return dictionary

    def as_nexus(self, nexus_node, error_collector: List[str]):
        super().as_nexus(nexus_node, error_collector)
