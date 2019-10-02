from nexus_constructor.component import Component
from nexus_constructor.chopper_component import ChopperComponent
from nexus_constructor.component_type import CHOPPER_CLASS_NAME
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
import h5py


def create_component(
    nexus_wrapper: NexusWrapper, component_group: h5py.Group
) -> Component:
    if (
        nexus_wrapper.get_attribute_value(component_group, "NX_class")
        == CHOPPER_CLASS_NAME
    ):
        return ChopperComponent(nexus_wrapper, component_group)
    return Component(nexus_wrapper, component_group)
