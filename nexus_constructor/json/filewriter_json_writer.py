from io import FileIO
from typing import Union, Any
import h5py
from nexus_constructor.common_attrs import CommonAttrs

NexusObject = Union[h5py.Group, h5py.Dataset, h5py.SoftLink]


def write_nexus_structure_to_json(data: Any, file: FileIO):
    """
    Generates and writes the nexus structure to a given JSON file object.
    The json description can be used by the file writer (github.com/ess-dmsc/kafka-to-nexus) to create a NeXus file

    :param data: The full description of the beamline and data
    :param file: the file object to output the JSON to.
    """
    raise NotImplementedError


def cast_to_int(data):
    """
    Python 3+ has an unlimited-size integer representation
    We can convert any numpy integer type to Python int for serialising to JSON
    """
    if isinstance(data, list):
        return data
    else:
        return int(data)


ATTR_NAME_BLACKLIST = [CommonAttrs.DEPENDEE_OF, CommonAttrs.UI_VALUE]
