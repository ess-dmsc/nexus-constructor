import attr
from nexus_constructor.component_type import ComponentType
from nexus_constructor.transformations import Transformation
from nexus_constructor.pixel_data import PixelData
from nexus_constructor.geometry_types import Geometry
from typing import List
from nexus_constructor.nexus_model import create_group, get_nx_class_for_component


def create_component(
    component_type,
    name,
    parent_group,
    description="",
    transform_parent=None,
    dependent_transform=None,
    transforms=None,
    geometry=None,
    pixel_data=None,
):
    """
    Factory function for creating components
    :param component_type: The type of component to create.
    :param name: The name of the component.
    :param description: Brief description of the component.
    :param transform_parent: The transform parent of the component to base transforms on.
    :param dependent_transform: The
    :param transforms: The transforms for this component.
    :param geometry: The geometry information.
    :param pixel_data: The pixel mapping information.
    :param parent_group: The parent HDF group to add the component to.
    :return: The created component object.
    """
    if transforms is None:
        transforms = []
    return Component(
        component_type=component_type,
        name=name,
        description=description,
        transform_parent=transform_parent,
        dependent_transform=dependent_transform,
        transforms=transforms,
        geometry=geometry,
        pixel_data=pixel_data,
        component_group=create_group(
            name, get_nx_class_for_component(component_type), parent_group
        ),
    )


@attr.s
class Component:
    """Components of an instrument"""

    component_type = attr.ib(ComponentType)
    name = attr.ib(str)
    description = attr.ib(default="", type=str)
    transform_parent = attr.ib(default=None, type=object)
    dependent_transform = attr.ib(default=None, type=Transformation)
    transforms = attr.ib(factory=list, type=List[Transformation])
    geometry = attr.ib(default=None, type=Geometry)
    pixel_data = attr.ib(default=None, type=PixelData)
    component_group = attr.ib(default=None)
