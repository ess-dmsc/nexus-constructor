import json
import h5py
import numpy as np
import uuid
from typing import Union, List

"""
Read the JSON and construct an in-memory NeXus file from the nexus_structure field
"""
JsonValue = Union[List, str, float, int, dict]
NexusObject = Union[h5py.Group, h5py.Dataset]


_json_type_to_numpy = {
    "string": h5py.special_dtype(vlen=str),
    "float": np.float32,
    "double": np.float64,
    "int32": np.int32,
    "int64": np.int64,
    "uint32": np.uint32,
    "uint64": np.uint64,
}

TYPE = "type"


def _add_to_nexus(children: List[dict], current_group: h5py.Group):
    """
    Go top down through JSON description constructing NeXus file
    """
    for child in children:
        if child[TYPE] == "group":
            _add_group(child, current_group)
        elif child[TYPE] == "dataset":
            _add_dataset(child, current_group)
        elif child[TYPE] == "stream":
            _add_stream(child, current_group)
        elif child[TYPE] == "link":
            _add_link(child, current_group)


def _add_stream(json_object: dict, current_group: h5py.Group):
    stream_group = current_group.create_group(json_object["stream"]["source"])
    stream_group.attrs["NX_class"] = "NCstream"
    add_datasets(json_object["stream"], stream_group)


def add_datasets(json_object: dict, stream_group: h5py.Group):
    for field_name, field_value in json_object.items():
        if isinstance(field_value, dict):
            new_group = stream_group.create_group(field_name)
            add_datasets(field_value, new_group)
        else:
            stream_group.create_dataset(name=field_name, data=field_value)


def _add_link(json_object: dict, current_group: h5py.Group):
    current_group[json_object["name"]] = h5py.SoftLink(json_object["target"])


def _add_dataset(json_object: dict, current_group: h5py.Group):
    numpy_type = _json_type_to_numpy[json_object["dataset"][TYPE]]
    values = json_object["values"]
    if json_object["dataset"][TYPE] == "string" and isinstance(
        json_object["values"], list
    ):
        values = [value.encode("utf8") for value in json_object["values"]]
    new_dataset = current_group.create_dataset(
        json_object["name"], dtype=numpy_type, data=values
    )
    _add_attributes(json_object, new_dataset)


def _add_group(json_object: dict, current_group: h5py.Group):
    new_group = current_group.create_group(json_object["name"])
    _add_attributes(json_object, new_group)
    _add_to_nexus(json_object["children"], new_group)


def _add_attributes(json_object: dict, nexus_object: NexusObject):
    if "attributes" in json_object:
        for attribute in json_object["attributes"]:
            nexus_object.attrs[attribute["name"]] = attribute["values"]


def _create_in_memory_file(filename: str) -> h5py.File:
    return h5py.File(filename, mode="x", driver="core", backing_store=False)


def json_to_nexus(json_input: str) -> h5py.File:
    """
    Convert JSON to in-memory NeXus file
    :param json_input:
    :return: NeXus file and any warning messages produced from validating the JSON
    """
    if not json_input:
        raise ValueError("Empty json string, nothing to load!")

    json_data = json.loads(json_input)
    nexus_file = _create_in_memory_file(str(uuid.uuid4()))

    nexus_structure = json_data["nexus_structure"]
    _add_to_nexus(nexus_structure["children"], nexus_file)

    return nexus_file
