import json
from typing import Union, List

from nexus_constructor.nexus.nexus_wrapper import NexusWrapper

"""
Read the JSON and construct an in-memory NeXus file from the nexus_structure field
"""
JsonValue = Union[List, str, float, int, dict]


def _add_to_nexus(children: JsonValue, wrapper: NexusWrapper):
    """
    Go top down through JSON description constructing NeXus file
    """
    for child in children:
        pass


def json_to_nexus(json_input: str) -> NexusWrapper:
    """
    Convert JSON to in-memory NeXus file
    :param json_input:
    :return: NeXus file and any warning messages produced from validating the JSON
    """

    if not json_input:
        raise ValueError("Empty json string, nothing to load!")

    json_data = json.loads(json_input)

    wrapper = NexusWrapper("json_to_nexus")
    try:
        nexus_structure = json_data["nexus_structure"]
        _add_to_nexus(nexus_structure["children"], wrapper)
    except:
        raise Exception("Error trying to parse nexus_structure")

    return wrapper
