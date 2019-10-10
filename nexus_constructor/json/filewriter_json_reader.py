import json
import h5py
import numpy as np
from typing import Union, List

"""
Read the JSON and construct an in-memory NeXus file from the nexus_structure field
"""
JsonValue = Union[List, str, float, int, dict]
NexusObject = Union[h5py.Group, h5py.Dataset]


_json_type_to_numpy = {
    "string": str,
    "float": np.float32,
    "double": np.float64,
    "int32": np.int32,
    "int64": np.int64,
    "uint32": np.uint32,
    "uint64": np.uint64,
}


def _add_to_nexus(children: List[dict], current_group: h5py.Group):
    """
    Go top down through JSON description constructing NeXus file
    """
    for child in children:
        if child["type"] == "group":
            _add_group(child, current_group)
        if child["type"] == "dataset":
            _add_dataset(child, current_group)


def _add_dataset(json_object: dict, current_group: h5py.Group):
    numpy_type = _json_type_to_numpy[json_object["dataset"]["type"]]
    new_dataset = current_group.create_dataset(
        json_object["name"], dtype=numpy_type, data=json_object["values"]
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


def _create_in_memory_file(filename):
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
    nexus_file = _create_in_memory_file("json_to_nexus")

    try:
        nexus_structure = json_data["nexus_structure"]
        _add_to_nexus(nexus_structure["children"], nexus_file)
    except:
        raise Exception("Error trying to parse nexus_structure")

    return nexus_file
