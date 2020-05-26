from typing import Any

"""
Read the JSON and construct a python model based on the structure.
"""


def json_to_nexus(json_input: str) -> Any:
    """
    Convert JSON to in-memory NeXus file
    :param json_input:
    :return: NeXus file and any warning messages produced from validating the JSON
    """
    if not json_input:
        raise ValueError("Empty json string, nothing to load!")
    raise NotImplementedError
