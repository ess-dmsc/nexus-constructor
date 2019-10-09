from nexus_constructor.nexus.nexus_wrapper import NexusWrapper

"""
Read the JSON and construct an in-memory NeXus file from it
"""


def json_to_nexus(json_input: str):
    wrapper = NexusWrapper("json_to_nexus")

    # Go through json, top down
