import json
import h5py
from typing import Union, List

"""
Read the JSON and construct an in-memory NeXus file from the nexus_structure field
"""
JsonValue = Union[List, str, float, int, dict]


def _add_to_nexus(children: List[dict], current_group: h5py.Group):
    """
    Go top down through JSON description constructing NeXus file
    """
    for child in children:
        if child["type"] == "group":
            _add_group(child, current_group)


def _add_group(child, current_group):
    new_group = current_group.create_group(child["name"])
    for attribute in child["attributes"]:
        new_group.attrs[attribute["name"]] = attribute["values"]
    _add_to_nexus(child["children"], new_group)


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
