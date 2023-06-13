import logging
from typing import TYPE_CHECKING, Callable, List, Tuple, Union

import numpy as np

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.invalid_field_names import INVALID_FIELD_NAMES
from nexus_constructor.model.group import Group
from nexus_constructor.model.module import (
    Dataset,
    FileWriterModule,
    Link,
    StreamModule,
    FileWriter,
)
from nexus_constructor.model.value_type import ValueTypes
from nexus_constructor.utils.required_component_fields import required_component_fields
from nexus_constructor.validators import FieldType

if TYPE_CHECKING:
    from PySide6.QtWidgets import QFrame  # noqa: F401

    from nexus_constructor.model.module import HS01Stream  # noqa: F401
    from nexus_constructor.model.value_type import ValueType  # noqa: F401
    from nexus_constructor.stream_fields_widget import StreamFieldsWidget  # noqa: F401


def update_existing_link_field(field: Link, new_ui_field: "QFrame"):
    """
    Fill in a UI link field for an existing link in the component
    :param field: The link field in the component group
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType.link
    new_ui_field.name = field.name
    new_ui_field.value = field.source


def update_existing_array_field(field: Dataset, new_ui_field: FieldWidget):
    """
    Fill in a UI array field for an existing array field in the component group
    :param field: The dataset to copy to the UI fields list model
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType(FieldType.array_dataset.value)
    __update_existing_dataset_field(field, new_ui_field)


def __update_existing_dataset_field(field: Dataset, new_ui_field: FieldWidget):
    new_ui_field.name = field.name
    new_ui_field.dtype = ValueTypes.STRING if not field.type else field.type
    new_ui_field.value = field.values  # type: ignore
    new_ui_field.attrs = field
    units = field.attributes.get_attribute_value(CommonAttrs.UNITS)
    new_ui_field.units = units or ""


def update_existing_filewriter_field(field: Dataset, new_ui_field: FieldWidget):
    """
    Fill in a UI filewriter field for an existing filewriter field in the component group
    :param field: The dataset to copy into the ???value line edit
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType(FieldType.filewriter.value)
    __update_existing_dataset_field(field, new_ui_field)


def update_existing_scalar_field(field: Dataset, new_ui_field: FieldWidget):
    """
    Fill in a UI scalar field for an existing scalar field in the component group
    :param field: The dataset to copy into the value line edit
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType(FieldType.scalar_dataset.value)
    __update_existing_dataset_field(field, new_ui_field)


def update_existing_stream_field(
    field: StreamModule, new_ui_field: "StreamFieldsWidget"
):
    """
    Fill in a UI stream field for an existing stream field in the component group
    :param field: The dataset to copy into the value line edit
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType.kafka_stream
    new_ui_field._old_schema = field.writer_module
    new_ui_field.streams_widget.update_existing_stream_info(field)
    new_ui_field.attrs = field
    units = field.attributes.get_attribute_value(CommonAttrs.UNITS)
    new_ui_field.units = units


def get_fields_with_update_functions(
    component: Group,
) -> List[Tuple[Union["FileWriterModule", "Group"], Callable]]:
    """
    Return a list of fields in a given component group.
    :param component: The component to check for fields
    :return: A list of a fields, regardless of field type
    """
    items_with_update_functions = []
    for item in component.children:
        update_function = find_field_type(item)
        items_with_update_functions.append((item, update_function))
    add_required_component_fields(component, items_with_update_functions)
    return items_with_update_functions


def add_required_component_fields(component: Group, items_with_update_functions):
    if component.nx_class in required_component_fields:
        datasets_config: List = required_component_fields[component.nx_class]
        for name, data_type, values, units in datasets_config:
            if not component[name]:
                dataset = Dataset(
                    name=name, parent_node=None, values=values, type=data_type
                )
                dataset.attributes.set_attribute_value(CommonAttrs.UNITS, units)
                find_field_type(dataset)
                items_with_update_functions.append((dataset, find_field_type(dataset)))


def find_field_type(item: "ValueType", ignore_names=INVALID_FIELD_NAMES) -> Callable:
    if isinstance(item, Dataset) and item.name not in ignore_names:
        if np.isscalar(item.values):
            return update_existing_scalar_field
        else:
            return update_existing_array_field
    elif isinstance(item, StreamModule):
        return update_existing_stream_field
    elif isinstance(item, Link):
        return update_existing_link_field
    elif isinstance(item, FileWriter):
        return update_existing_filewriter_field
    else:
        try:
            logging.debug(
                f"Object {item.name} not handled as field - could be used for other parts of UI instead."  # type: ignore
            )
        except Exception:
            logging.debug(
                "Encountered object that is not handled as field - could be used for other parts of UI instead."
            )
    return None
