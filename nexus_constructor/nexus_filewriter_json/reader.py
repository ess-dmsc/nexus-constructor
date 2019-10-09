import json

from nexus_constructor.nexus.nexus_wrapper import NexusWrapper

"""
Read the JSON and construct an in-memory NeXus file from the nexus_structure field
"""


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

    return wrapper
