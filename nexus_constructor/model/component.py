from typing import Tuple, Union

import attr
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtGui import QMatrix4x4, QVector3D

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.group import Group, Dataset, DatasetMetadata
from nexus_constructor.model.helpers import (
    get_item,
    set_attribute_value,
    get_attribute_value,
)
from nexus_constructor.model.transformation import Transformation, TransformationGroup
from nexus_constructor.pixel_data import PixelGrid, PixelMapping
from nexus_constructor.pixel_data_to_nexus_utils import (
    get_detector_number_from_pixel_mapping,
)
from nexus_constructor.transformation_types import TransformationType


def _generate_incremental_name(base_name, group):
    number = 1
    while get_item(group.children, f"{base_name}_{number}") is not None:
        number += 1
    return f"{base_name}_{number}"


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


@attr.s
class Component(Group):
    """
    Base class for a component object. In the NeXus file this would translate to the component group.
    """

    def __init__(self, name, description, nx_class, pixel_data=None):
        self.name = name
        self.description = description
        self.nx_class = nx_class

        if pixel_data is not None:
            raise NotImplementedError

    @property
    def description(self):
        return get_attribute_value(self.children, CommonAttrs.DESCRIPTION)

    @description.setter
    def description(self, new_description: str):
        set_attribute_value(self.children, CommonAttrs.DESCRIPTION, new_description)

    @property
    def transform(self):
        """
        Creates a QTransform based on the full chain of transforms this component points to.
        :return: QTransform of final transformation
        """
        transform_matrix = QMatrix4x4()
        for transform in self.transforms_full_chain:
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
        raise NotImplementedError
        # transforms = TransformationsList(self)
        # depends_on = self.get_field(CommonAttrs.DEPENDS_ON)
        # self._get_transform(depends_on, transforms, local_only=True)
        # return transforms

    @property
    def transforms_full_chain(self):
        """
        Gets all transforms in the depends_on chain for this component
        :return: List of transforms
        """
        raise NotImplementedError
        # transforms = TransformationsList(self)
        # depends_on = self.get_field(CommonAttrs.DEPENDS_ON)
        # self._get_transform(depends_on, transforms)
        # return transforms

    def add_translation(
        self, vector: QVector3D, name: str = None, depends_on: Transformation = None
    ) -> Transformation:
        """
        Note, currently assumes translation is in metres
        :param vector: direction and magnitude of translation as a 3D vector
        :param name: name of the translation group (Optional)
        :param depends_on: existing transformation which the new one depends on (otherwise relative to origin)
        """
        unit_vector, magnitude = _normalise(vector)
        return self._create_transform(
            name,
            TransformationType.TRANSLATION,
            magnitude,
            "m",
            unit_vector,
            depends_on,
        )

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
        return self._create_transform(
            name, TransformationType.ROTATION, angle, "degrees", axis, depends_on
        )

    def _create_transform(
        self,
        name: str,
        transformation_type: TransformationType,
        angle_or_magnitude: float,
        units: str,
        vector: QVector3D,
        depends_on: Transformation,
    ):
        transforms_group = self.__create_transformations_group_if_does_not_exist()
        if name is None:
            name = _generate_incremental_name(transformation_type, transforms_group)
        transform = Transformation(name, angle_or_magnitude)
        transform.type = transformation_type
        transform.ui_value = angle_or_magnitude
        transform.units = units
        transform.vector = vector
        transform.depends_on = depends_on
        return transform

    def __create_transformations_group_if_does_not_exist(self) -> TransformationGroup:
        for item in self.children:
            if isinstance(item, TransformationGroup):
                return item
        group = TransformationGroup()
        self.children.append(group, name="transformations")
        return group

    @property
    def shape(self):
        raise NotImplementedError

    def remove_shape(self):
        raise NotImplementedError

    def set_off_shape(
        self, loaded_geometry, units: str = "", filename: str = "", pixel_data=None,
    ):
        raise NotImplementedError

    def set_cylinder_shape(
        self,
        axis_direction: QVector3D = QVector3D(0.0, 0.0, 1.0),
        height: float = 1.0,
        radius: float = 1.0,
        units: Union[str, bytes] = "m",
        pixel_data=None,
    ):
        raise NotImplementedError

    def record_pixel_grid(self, pixel_grid: PixelGrid):
        """
        Records the pixel grid data to the NeXus file.
        :param pixel_grid: The PixelGrid created from the input provided to the Add/Edit Component Window.
        """
        raise NotImplementedError

    def record_pixel_mapping(self, pixel_mapping: PixelMapping):
        """
        Records the pixel mapping data to the NeXus file.
        :param pixel_mapping: The PixelMapping created from the input provided to the Add/Edit Component Window.
        """
        detector_number = Dataset("detector_number", DatasetMetadata([1], "int64"))
        detector_number.values = get_detector_number_from_pixel_mapping(
            pixel_mapping
        )  # TODO create a helper for setting dataset values, size should be derived from the inputted 'values'

    def clear_pixel_data(self):
        raise NotImplementedError
