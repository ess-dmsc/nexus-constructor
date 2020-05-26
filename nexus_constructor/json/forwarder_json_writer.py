from typing import TextIO

import h5py
from nexus_constructor.model.stream import WriterModules

FORWARDER_SCHEMAS = [WriterModules.F142.value, WriterModules.TDCTIME.value]


def generate_forwarder_command(
    output_file: TextIO, root: h5py.Group, provider_type: str, default_broker: str
):
    """
    Generate a forwarder command containing a list of PVs and which topics to route them to.
    :param output_file: file object to write the JSON output to.
    :param streams: dictionary of stream objects.
    :param provider_type: whether to use channel access or pv access protocol
    """
    raise NotImplementedError
