import attr
from nexus_constructor.component_type import ComponentType
from nexus_constructor.data_model import Transformation, PixelData
from nexus_constructor.geometry_types import Geometry
from typing import List
from nexus_constructor.nexus_model import create_group, get_nx_class_for_component


def create_component(
    component_type,
    name,
    description,
    transform_parent,
    dependent_transform,
    transforms,
    geometry,
    pixel_data,
    parent_group,
):
    """
    Factory function for creating components
    :param component_type: The type of component to create.
    :param name: The name of the component.
    :param description: Brief description of the component.
    :param transform_parent: The transform parent of the component to base transforms on.
    :param dependent_transform: The
    :param transforms: The transforms for this component.
    :param geometry:
    :param pixel_data:
    :param parent_group:
    :return:
    """
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
