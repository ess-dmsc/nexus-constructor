from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.component import Component
from uuid import uuid1
import h5py
from typing import Any, Tuple


def create_nexus_wrapper() -> NexusWrapper:
    return NexusWrapper(str(uuid1()))


def add_component_to_file(
    nexus_wrapper: NexusWrapper,
    field_name: str,
    field_value: Any,
    component_name: str = "test_component",
) -> Tuple[h5py.Group, Component]:
    component_group = nexus_wrapper.nexus_file.create_group(component_name)
    component_group.create_dataset(field_name, data=field_value)
    component = Component(nexus_wrapper, component_group)
    return component_group, component
