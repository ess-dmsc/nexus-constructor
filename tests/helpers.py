from typing import Any
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset, DatasetMetadata
from nexus_constructor.validators import DATASET_TYPE


def add_component_to_file(
    field_name: str = "test_field",
    field_value: Any = 42,
    component_name: str = "test_component",
) -> Component:
    component = Component(name=component_name)
    component.set_field_value(
        name=field_name,
        value=Dataset(
            name=field_name,
            dataset=DatasetMetadata(type=DATASET_TYPE["Double"]),
            values=field_value,
        ),
    )
    return component
