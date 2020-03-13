from typing import Any
from nexus_constructor.component.component import Component
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper


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
