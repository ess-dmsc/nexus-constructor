from nexus_constructor.nexus.nexus_wrapper import NexusWrapper

"""
Read the JSON and construct an in-memory NeXus file from it
"""


def json_to_nexus(json_input: str) -> NexusWrapper:
    if not json_input:
        raise ValueError("Empty json string, nothing to load!")

    wrapper = NexusWrapper("json_to_nexus")

    return wrapper
