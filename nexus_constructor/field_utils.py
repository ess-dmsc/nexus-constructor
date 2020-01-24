import logging
from typing import List

import h5py
import numpy as np

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.invalid_field_names import INVALID_FIELD_NAMES
from nexus_constructor.nexus.nexus_wrapper import get_name_of_node
from nexus_constructor.validators import FieldType


def update_existing_link_field(field: h5py.SoftLink, new_ui_field: FieldWidget):
    """
    Fill in a UI link field for an existing link in the component
    :param field: The link field in the component group
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType.link.value
    new_ui_field.value = field.parent.get(field.name, getlink=True).path


def update_existing_array_field(field: h5py.Dataset, new_ui_field: FieldWidget):
    """
    Fill in a UI array field for an existing array field in the component group
    :param value: The array dataset's value to copy to the UI fields list model
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.dtype = field.dtype
    new_ui_field.field_type = FieldType.array_dataset.value
    new_ui_field.value = field[()]


def update_existing_scalar_field(field: h5py.Dataset, new_ui_field: FieldWidget):
    """
    Fill in a UI scalar field for an existing scalar field in the component group
    :param field: The dataset to copy into the value line edit
    :param new_ui_field: The new UI field to fill in with existing data
    """
    dtype = field.dtype
    if "S" in str(dtype):
        dtype = h5py.special_dtype(vlen=str)
        new_ui_field.value = field[()]
    else:
        new_ui_field.value = field[()]
    new_ui_field.dtype = dtype
    new_ui_field.field_type = FieldType.scalar_dataset.value


def update_existing_stream_field(field: h5py.Dataset, new_ui_field: FieldWidget):
    """
    Fill in a UI stream field for an existing stream field in the component group
    :param field: The dataset to copy into the value line edit
    :param new_ui_field: The new UI field to fill in with existing data
    """
    new_ui_field.field_type = FieldType.kafka_stream.value
    new_ui_field.streams_widget.update_existing_stream_info(field)


def get_fields_with_update_functions(
    group: h5py.Group,
) -> (List[h5py.Dataset], List[h5py.Dataset], List[h5py.Group], List[h5py.Group]):
    """
    Return a list of fields in a given component group.
    :param group: The hdf5 component group to check for fields
    :return: A list of a fields, regardless of field type
    """
    items_with_update_functions = {}
    for item in group.values():
        item, update_function = find_field_type(item)
        items_with_update_functions[item] = update_function
    return items_with_update_functions


def find_field_type(item):
    if (
        isinstance(item, h5py.Dataset)
        and get_name_of_node(item) not in INVALID_FIELD_NAMES
    ):
        if np.isscalar(item[()]):
            return item, update_existing_scalar_field
        else:
            return item, update_existing_array_field

    elif isinstance(item, h5py.Group):
        if isinstance(item.parent.get(item.name, getlink=True), h5py.SoftLink):
            return item, update_existing_link_field
        elif (
            CommonAttrs.NX_CLASS in item.attrs.keys()
            and item.attrs[CommonAttrs.NX_CLASS] == "NCstream"
        ):
            return item, update_existing_stream_field
    logging.debug(
        f"Object {get_name_of_node(item)} not handled as field - could be used for other parts of UI instead"
    )
    return item, None
