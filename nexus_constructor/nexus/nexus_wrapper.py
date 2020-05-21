from typing import Any, Optional

import h5py

from nexus_constructor.common_attrs import CommonAttrs


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
