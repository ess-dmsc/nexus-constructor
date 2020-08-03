from typing import Any
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.value_type import ValueTypes


def add_component_to_file(
    field_name: str = "test_field",
    field_value: Any = 42,
    component_name: str = "test_component",
) -> Component:
    component = Component(name=component_name)
    component.set_field_value(
        name=field_name,
        value=Dataset(
            name=field_name, type=ValueTypes.DOUBLE, size="1", values=field_value
        ),
        dtype=ValueTypes.DOUBLE,
    )
    return component
