import attr
import h5py
from typing import Any, List
from nexus_constructor.pixel_data import PixelData
from nexus_constructor.geometry_types import Geometry
from nexus_constructor.nexus import nexus_wrapper as nx
from nexus_constructor.transformations import Transformation, create_transform


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

    def _get_transform(self, depends_on: str, transforms: List[Transformation]):
        """
        Recursive function, appends each transform in depends_on chain to transforms list
        """
        if depends_on and depends_on != ".":
            transform_dataset = self.file.nexus_file[depends_on]
            transforms.append(
                create_transform(
                    transform_dataset.attrs["type"],
                    transform_dataset["vector"],
                    transform_dataset[...],
                )
            )
            if "depends_on" in transform_dataset.attrs.keys():
                self._get_transform(transform_dataset.attrs["depends_on"], transforms)


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
