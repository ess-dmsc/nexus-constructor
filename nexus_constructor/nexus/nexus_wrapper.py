import logging
import uuid
import h5py
from PySide2.QtCore import Signal, QObject
from typing import Any, TypeVar, Optional
import numpy as np

from nexus_constructor.common_attrs import CommonAttrs

DEFAULT_INSTRUMENT = "instrument"
DEFAULT_ENTRY = "entry"


def set_up_in_memory_nexus_file(filename: str) -> h5py.File:
    """
    Creates an in-memory nexus-file to store the model data in.
    :return: The file object.
    """
    return h5py.File(filename, mode="x", driver="core", backing_store=False)


def append_nxs_extension(file_name: str) -> str:
    extension = ".nxs"
    if file_name.endswith(extension):
        return file_name
    else:
        return file_name + extension


def get_nx_class(group: h5py.Group) -> Optional[str]:
    if CommonAttrs.NX_CLASS not in group.attrs.keys():
        return None

    nx_class = group.attrs[CommonAttrs.NX_CLASS]
    return to_string(nx_class)


def to_string(input_to_convert: Any) -> str:
    """
    Converts to string, assumes utf-8 encoding for bytes
    Input can be bytes, str, numpy array
    :param input_to_convert: Dataset value to convert
    :return: str
    """
    if isinstance(input_to_convert, bytes):
        return input_to_convert.decode("utf-8")
    return str(input_to_convert)


def create_temporary_in_memory_file() -> h5py.File:
    """
    Create a temporary in-memory nexus file with a random name.
    :return: The file object
    """
    return set_up_in_memory_nexus_file(str(uuid.uuid4()))

