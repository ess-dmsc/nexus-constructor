from nexus_constructor.component.component import Component
from nexus_constructor.component.chopper_shape import ChopperShape
from nexus_constructor.component.pixel_shape import PixelShape
from nexus_constructor.component.component_type import (
    CHOPPER_CLASS_NAME,
    PIXEL_COMPONENT_TYPES,
)
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper, get_nx_class
import h5py


def create_component(
    nexus_wrapper: NexusWrapper, component_group: h5py.Group
) -> Component:
    nx_class = get_nx_class(component_group)
    if nx_class == CHOPPER_CLASS_NAME:
        return Component(
            nexus_wrapper, component_group, ChopperShape(nexus_wrapper, component_group)
        )
    if nx_class in PIXEL_COMPONENT_TYPES and "pixel_shape" in component_group:
        return Component(
            nexus_wrapper, component_group, PixelShape(nexus_wrapper, component_group)
        )
    return Component(nexus_wrapper, component_group)
