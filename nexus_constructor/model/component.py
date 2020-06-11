import logging
from typing import Tuple, Union, List, Dict, Any, Optional
import attr
import numpy as np
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtGui import QMatrix4x4, QVector3D
from PySide2.QtWidgets import QListWidget

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.component.transformations_list import TransformationsList
from nexus_constructor.geometry.utils import validate_nonzero_qvector
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.geometry import (
    CylindricalGeometry,
    OFFGeometryNexus,
    NoShapeGeometry,
    OFFGeometry,
)
from nexus_constructor.model.group import Group
from nexus_constructor.model.node import _generate_incremental_name
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.pixel_data import PixelGrid, PixelMapping, PixelData
from nexus_constructor.pixel_data_to_nexus_utils import (
    get_detector_number_from_pixel_mapping,
    get_x_offsets_from_pixel_grid,
    get_y_offsets_from_pixel_grid,
    get_z_offsets_from_pixel_grid,
    get_detector_ids_from_pixel_grid,
    PIXEL_FIELDS,
    get_detector_faces_from_pixel_mapping,
)
from nexus_constructor.transformation_types import TransformationType
from nexus_constructor.ui_utils import show_warning_dialog

TRANSFORMS_GROUP_NAME = "transformations"


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

    transforms_list = attr.ib(factory=list)

    @property
    def description(self):
        try:
            return self.get_field_value(CommonAttrs.DESCRIPTION)
        except AttributeError:
            return ""

    @description.setter
    def description(self, new_description: str):
        self.set_field_value(CommonAttrs.DESCRIPTION, new_description)

    @property
    def transform(self):
        """
        Creates a QTransform based on the full chain of transforms this component points to.
        :return: QTransform of final transformation
        """
        transform_matrix = QMatrix4x4()
        for transform in self.transforms:
            transform_matrix *= transform.qmatrix
        transformation = Qt3DCore.QTransform()
        transformation.setMatrix(transform_matrix)
        return transformation

    @property
    def transforms(self):
        """
        Gets transforms in the depends_on chain but only those which are local to
        this component's group in the NeXus file
        :return:
        """
        transforms = TransformationsList(self)
        for i in self.transforms_list:
            transforms.append(i)

        return transforms

    def _get_transform(
        self,
        depends_on: Transformation,
        transforms: List[Transformation],
        local_only: bool = False,
    ):
        """
        Recursive function, appends each transform in depends_on chain to transforms list
        :param depends_on: The next depends_on string to find the next transformation in the chain
        :param transforms: The list to populate with transformations
        :param local_only: If True then only add transformations which are stored within this component
        """
        if depends_on is not None:
            if local_only:
                return
            transforms.append(depends_on)
            self._get_transform(depends_on.depends_on, transforms, local_only)

    @property
    def transforms_full_chain(self):
        """
        Gets all transforms in the depends_on chain for this component
        :return: List of transforms
        """
        transforms = TransformationsList(self)
        try:
            depends_on = self.get_field_value(CommonAttrs.DEPENDS_ON)
        except AttributeError:
            depends_on = None
        self._get_transform(depends_on, transforms, local_only=False)
        return transforms

    def add_translation(
        self,
        vector: QVector3D,
        name: str = None,
        depends_on: Transformation = None,
        values: Dataset = Dataset("", None, []),
    ) -> Transformation:
        """
        Note, currently assumes translation is in metres
        :param vector: direction and magnitude of translation as a 3D vector
        :param name: name of the translation group (Optional)
        :param depends_on: existing transformation which the new one depends on (otherwise relative to origin)
        :param values: The translation distance information.
        """
        unit_vector, _ = _normalise(vector)
        return self._create_transform(
            name,
            TransformationType.TRANSLATION,
            0.0,
            "m",
            unit_vector,
            depends_on,
            values,
        )

    def add_rotation(
        self,
        axis: QVector3D,
        angle: float,
        name: str = None,
        depends_on: Transformation = None,
        values: Dataset = Dataset("", None, []),
    ) -> Transformation:
        """
        Note, currently assumes angle is in degrees
        :param axis: axis
        :param angle:
        :param name: Name of the rotation group (Optional)
        :param depends_on: existing transformation which the new one depends on (otherwise relative to origin)
        :param values: The translation distance information.
        """
        return self._create_transform(
            name,
            TransformationType.ROTATION,
            angle,
            "degrees",
            axis,
            depends_on,
            values,
        )

    def _create_transform(
        self,
        name: str,
        transformation_type: TransformationType,
        angle_or_magnitude: float,
        units: str,
        vector: QVector3D,
        depends_on: Transformation,
        values: Dataset,
    ):
        if name is None:
            name = _generate_incremental_name(transformation_type, self.transforms_list)
        transform = Transformation(name, angle_or_magnitude)
        transform.type = transformation_type
        transform.ui_value = angle_or_magnitude
        transform.units = units
        transform.vector = vector
        transform.depends_on = depends_on
        transform.values = values
        self.transforms_list.append(transform)
        return transform

    def remove_transformation(self, transform: Transformation):
        if transform.dependents:
            raise Exception
        self.transforms_list.remove(transform)

    @property
    def shape(self):
        if PIXEL_SHAPE_GROUP_NAME in self:
            return (
                self[PIXEL_SHAPE_GROUP_NAME],
                self._create_transformation_vectors_for_pixel_offsets(),
            )
        if SHAPE_GROUP_NAME in self:
            return self[SHAPE_GROUP_NAME], None
        return NoShapeGeometry(), None

    def remove_shape(self):
        for group_name in [PIXEL_SHAPE_GROUP_NAME, SHAPE_GROUP_NAME]:
            if group_name in self:
                del self[SHAPE_GROUP_NAME]

    def set_off_shape(
        self,
        loaded_geometry: OFFGeometry,
        units: str = "",
        filename: str = "",
        pixel_data=None,
    ):
        self.remove_shape()

        shape_group = _get_shape_group_for_pixel_data(pixel_data)
        geometry = OFFGeometryNexus(shape_group)
        geometry.nx_class = OFF_GEOMETRY_NX_CLASS
        geometry.record_faces(loaded_geometry.faces)
        geometry.record_vertices(loaded_geometry.vertices)
        geometry.units = units
        geometry.file_path = filename

        if isinstance(pixel_data, PixelMapping):
            geometry.detector_faces = get_detector_faces_from_pixel_mapping(pixel_data)

        self[shape_group] = geometry
        return geometry

    def set_cylinder_shape(
        self,
        axis_direction: QVector3D = QVector3D(0.0, 0.0, 1.0),
        height: float = 1.0,
        radius: float = 1.0,
        units: Union[str, bytes] = "m",
        pixel_data=None,
    ):
        self.remove_shape()
        validate_nonzero_qvector(axis_direction)
        shape_group = _get_shape_group_for_pixel_data(pixel_data)
        geometry = CylindricalGeometry(shape_group)
        geometry.nx_class = CYLINDRICAL_GEOMETRY_NX_CLASS

        vertices = CylindricalGeometry.calculate_vertices(
            axis_direction, height, radius
        )
        geometry.set_field_value(CommonAttrs.VERTICES, vertices)

        # # Specify 0th vertex is base centre, 1st is base edge, 2nd is top centre
        geometry.set_field_value("cylinders", np.array([0, 1, 2]))
        geometry[CommonAttrs.VERTICES].set_attribute_value(CommonAttrs.UNITS, units)

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

    def record_pixel_grid(self, pixel_grid: PixelGrid):
        """
        Records the pixel grid data to the NeXus file.
        :param pixel_grid: The PixelGrid created from the input provided to the Add/Edit Component Window.
        """
        self.set_field_value(
            "x_pixel_offset", get_x_offsets_from_pixel_grid(pixel_grid), "float64"
        )
        self.set_field_value(
            "y_pixel_offset", get_y_offsets_from_pixel_grid(pixel_grid), "float64"
        )
        self.set_field_value(
            "z_pixel_offset", get_z_offsets_from_pixel_grid(pixel_grid), "float64"
        )
        self.set_field_value(
            "detector_number", get_detector_ids_from_pixel_grid(pixel_grid), "int64"
        )

    def record_pixel_mapping(self, pixel_mapping: PixelMapping):
        """
        Records the pixel mapping data to the NeXus file.
        :param pixel_mapping: The PixelMapping created from the input provided to the Add/Edit Component Window.
        """
        self.set_field_value(
            "detector_number",
            get_detector_number_from_pixel_mapping(pixel_mapping),
            "int64",
        )

    def _create_transformation_vectors_for_pixel_offsets(
        self,
    ) -> Optional[List[QVector3D]]:
        """
        Construct a transformation (as a QVector3D) for each pixel offset
        """
        try:
            x_offsets = self.get_field_value("x_pixel_offset")
            y_offsets = self.get_field_value("y_pixel_offset")
        except AttributeError:
            logging.info(
                "In pixel_shape_component expected to find x_pixel_offset and y_pixel_offset datasets"
            )
            return
        try:
            z_offsets = self.get_field_value("z_pixel_offset")
        except AttributeError:
            z_offsets = np.zeros_like(x_offsets)
        # offsets datasets can be 2D to match dimensionality of detector, so flatten to 1D
        return [
            QVector3D(x, y, z)
            for x, y, z in zip(
                x_offsets.flatten(), y_offsets.flatten(), z_offsets.flatten()
            )
        ]

    def as_dict(self) -> Dict[str, Any]:
        dictionary = super(Component, self).as_dict()
        # Add transformations in a child group
        dictionary["children"].append(
            {
                "type": "group",
                "name": TRANSFORMS_GROUP_NAME,
                "children": [transform.as_dict() for transform in self.transforms_list],
            }
        )
        return dictionary


def add_fields_to_component(component: Component, fields_widget: QListWidget):
    """
    Adds fields from a list widget to a component.
    :param component: Component to add the field to.
    :param fields_widget: The field list widget to extract field information such the name and value of each field.
    """
    for i in range(fields_widget.count()):
        widget = fields_widget.itemWidget(fields_widget.item(i))
        try:
            component[widget.name] = widget.value
        except ValueError as error:
            show_warning_dialog(
                f"Warning: field {widget.name} not added",
                title="Field invalid",
                additional_info=str(error),
                parent=fields_widget.parent().parent(),
            )


SHAPE_GROUP_NAME = "shape"
PIXEL_SHAPE_GROUP_NAME = "pixel_shape"
CYLINDRICAL_GEOMETRY_NX_CLASS = "NXcylindrical_geometry"
OFF_GEOMETRY_NX_CLASS = "NXoff_geometry"
