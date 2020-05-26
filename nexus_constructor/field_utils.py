import logging
from typing import List, Callable, Tuple, Union

import numpy as np

from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.invalid_field_names import INVALID_FIELD_NAMES
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.link import Link
from nexus_constructor.model.stream import StreamGroup
from nexus_constructor.validators import FieldType


def update_existing_link_field(field: Link, new_ui_field: FieldWidget):
    """
    Fill in a UI link field for an existing link in the component
    :param field: The link field in the component group
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType.link.value
    new_ui_field.value = field.target


def update_existing_array_field(field: Dataset, new_ui_field: FieldWidget):
    """
    Fill in a UI array field for an existing array field in the component group
    :param value: The array dataset's value to copy to the UI fields list model
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType.array_dataset.value
    new_ui_field.dtype = field.dataset.type
    new_ui_field.value = field.values


def update_existing_scalar_field(field: Dataset, new_ui_field: FieldWidget):
    """
    Fill in a UI scalar field for an existing scalar field in the component group
    :param field: The dataset to copy into the value line edit
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType.scalar_dataset.value
    new_ui_field.value = field.values
    new_ui_field.dtype = field.dataset.type


def update_existing_stream_field(field: StreamGroup, new_ui_field: FieldWidget):
    """
    Fill in a UI stream field for an existing stream field in the component group
    :param field: The dataset to copy into the value line edit
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType.kafka_stream.value
    new_ui_field.streams_widget.update_existing_stream_info(field)


def get_fields_with_update_functions(
    component: Component,
) -> List[Tuple[Union[Dataset, Link, StreamGroup], Callable]]:
    """
    Return a list of fields in a given component group.
    :param field: The hdf5 component group to check for fields
    :return: A list of a fields, regardless of field type
    """
    items_with_update_functions = []
    for item in component.children:
        update_function = find_field_type(item)
        items_with_update_functions.append((item, update_function))
    return items_with_update_functions


def find_field_type(item: Union[Dataset, StreamGroup, Link]) -> Callable:
    if isinstance(item, Dataset) and item.name not in INVALID_FIELD_NAMES:
        if np.isscalar(item.values):
            return update_existing_scalar_field
        else:
            return update_existing_array_field
    elif isinstance(item, StreamGroup):
        return update_existing_stream_field
    elif isinstance(item, Link):
        return update_existing_link_field
    else:
        logging.debug(
            f"Object {item.name} not handled as field - could be used for other parts of UI instead"
        )
