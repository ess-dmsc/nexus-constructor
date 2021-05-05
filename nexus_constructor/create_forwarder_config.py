from typing import Any, List

from streaming_data_types.fbschemas.forwarder_config_update_rf5k.Protocol import (
    Protocol,
)
from streaming_data_types.fbschemas.forwarder_config_update_rf5k.UpdateType import (
    UpdateType,
)
from streaming_data_types.forwarder_config_update_rf5k import StreamInfo, serialise_rf5k

from nexus_constructor.model.group import Group
from nexus_constructor.model.model import Model
from nexus_constructor.model.stream import StreamGroup
from nexus_constructor.model.stream import Stream

provider_str_to_enum = {"pva": Protocol.PVA, "ca": Protocol.CA, "fake": Protocol.FAKE}


def _check_for_streams_in_children(
    streams: List[StreamInfo], parent: Any, protocol: Protocol
):
    """
    Recurse, go top-down through model looking for streams
    """
    for child in parent.children:
        if isinstance(child, StreamGroup):
            for stream in child.children:
                streams.append(
                    StreamInfo(
                        stream.source,
                        stream.writer_module,
                        stream.topic,
                        protocol,
                    )
                )
        elif isinstance(child, Group):
            _check_for_streams_in_children(streams, child, protocol)
    components = []
    try:
        components = parent.component_list
    except AttributeError:
        pass
    for component in components:
        _check_for_streams_in_children(streams, component, protocol)


def create_forwarder_config(model: Model, provider_type: str) -> bytes:
    protocol = provider_str_to_enum[provider_type]
    streams: List["Stream"] = []
    _check_for_streams_in_children(streams, model.entry, protocol)
    return serialise_rf5k(UpdateType.ADD, streams)
