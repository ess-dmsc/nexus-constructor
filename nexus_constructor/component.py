import attr
import h5py
import numpy as np
from typing import Any, List
from PySide2.QtGui import QVector3D
from nexus_constructor.pixel_data import PixelData
from nexus_constructor.geometry_types import Geometry
from nexus_constructor.nexus import nexus_wrapper as nx
from nexus_constructor.transformations import Transformation, TransformationModel


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


def _qvector3d_to_numpy_array(input_vector: QVector3D):
    return np.array([input_vector.x(), input_vector.y(), input_vector.z()]).astype(
        float
    )


def _generate_incremental_name(base_name, group: h5py.Group):
    number = 1
    while f"{base_name}_{number}" in group:
        number += 1
    return f"{base_name}_{number}"


class ComponentModel:
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

    def get_field(self, name: str):
        return self.file.get_field_value(self.group, name)

    def set_field(self, name: str, value: Any, dtype=None):
        self.file.set_field_value(self.group, name, value, dtype)

    @property
    def nx_class(self):
        return self.file.get_nx_class(self.group)

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
    def transforms(self):
        """
        Gets all transforms in the depends_on chain for this component
        :return: List of transforms
        """
        transforms = []
        depends_on = self.get_field("depends_on")
        self._get_transform(depends_on, transforms)
        return transforms

    def _get_transform(self, depends_on: str, transforms: List[TransformationModel]):
        """
        Recursive function, appends each transform in depends_on chain to transforms list
        """
        if depends_on and depends_on != ".":
            transform_dataset = self.file.nexus_file[depends_on]
            transforms.append(TransformationModel(self.file, transform_dataset))
            if "depends_on" in transform_dataset.attrs.keys():
                self._get_transform(transform_dataset.attrs["depends_on"], transforms)

    def add_translation(
        self,
        vector: QVector3D,
        name: str = None,
        depends_on: TransformationModel = None,
    ):
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
            field, "vector", _qvector3d_to_numpy_array(unit_vector)
        )
        self.file.set_attribute_value(field, "transformation_type", "Translation")
        if depends_on is None:
            self.file.set_attribute_value(field, "depends_on", ".")
        else:
            self.file.set_attribute_value(field, "depends_on", depends_on.dataset.name)
        return TransformationModel(self.file, field)

    def add_rotation(
        self,
        axis: QVector3D,
        angle: float,
        name: str = None,
        depends_on: TransformationModel = None,
    ):
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
        self.file.set_attribute_value(field, "vector", _qvector3d_to_numpy_array(axis))
        self.file.set_attribute_value(field, "transformation_type", "Rotation")
        if depends_on is None:
            self.file.set_attribute_value(field, "depends_on", ".")
        else:
            self.file.set_attribute_value(field, "depends_on", depends_on.dataset.name)
        return TransformationModel(self.file, field)

    def remove_transformation(self, transformation: TransformationModel):
        # Remove whole transformations group if this is the only transformation in it
        if len(transformation.dataset.parent.keys()) == 1:
            self.file.delete_node(transformation.dataset.parent)
        # Otherwise just remove the transformation from the group
        else:
            self.file.delete_node(transformation.dataset)

    @property
    def depends_on(self):
        depends_on_path = self.file.get_field_value(self.group, "depends_on")
        if depends_on_path is None:
            return None
        return TransformationModel(self.file, self.file[depends_on_path])

    @depends_on.setter
    def depends_on(self, transformation: TransformationModel):
        self.file.set_field_value(
            self.group, "depends_on", transformation.dataset.name, str
        )


@attr.s
class Component:
    """DEPRECATED: Switching to use ComponentModel everywhere"""

    nx_class = attr.ib(str)
    name = attr.ib(str)
    description = attr.ib(default="", type=str)
    transform_parent = attr.ib(default=None, type=object)
    dependent_transform = attr.ib(default=None, type=Transformation)
    transforms = attr.ib(factory=list, type=List[Transformation])
    geometry = attr.ib(default=None, type=Geometry)
    pixel_data = attr.ib(default=None, type=PixelData)
