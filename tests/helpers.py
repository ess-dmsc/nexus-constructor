from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.component import Component
from uuid import uuid1
from typing import Any
import h5py


def create_in_memory_file(filename):
    return h5py.File(filename, mode="x", driver="core", backing_store=False)


def create_nexus_wrapper() -> NexusWrapper:
    return NexusWrapper(str(uuid1()))


def add_component_to_file(
    nexus_wrapper: NexusWrapper,
    field_name: str = "test_field",
    field_value: Any = 42,
    component_name: str = "test_component",
) -> Component:
    component_group = nexus_wrapper.nexus_file.create_group(component_name)
    component_group.create_dataset(field_name, data=field_value)
    component = Component(nexus_wrapper, component_group)
    return component
