from streaming_data_types.fbschemas.forwarder_config_update_rf5k.UpdateType import (
    UpdateType,
)
from streaming_data_types.forwarder_config_update_rf5k import (
    StreamInfo,
    deserialise_rf5k,
)

from nexus_constructor.create_forwarder_config import create_forwarder_config
from nexus_constructor.model.component import Component
from nexus_constructor.model.model import Model
from nexus_constructor.model.stream import EV42Stream, F142Stream, StreamGroup


def test_create_forwarder_config_is_add_request():
    model = Model()
    component = Component("test_component", parent_node=model.entry.instrument)
    model.entry.instrument.component_list.append(component)
    stream_group = StreamGroup("test_stream_group")
    stream_group["test_stream"] = F142Stream("test_topic", "test_source", "double")
    component["test_stream_field"] = stream_group
    flatbuffer = create_forwarder_config(model, "pva")

    info_from_buffer = deserialise_rf5k(flatbuffer)
    assert info_from_buffer.config_change == UpdateType.ADD


def test_create_forwarder_config_serialises_streams_from_component_fields():
    model = Model()
    component = Component("test_component", parent_node=model.entry.instrument)
    model.entry.instrument.component_list.append(component)

    stream_group_1 = StreamGroup("test_stream_group")
    test_stream_1 = F142Stream("test_topic", "test_source", "double")
    test_stream_1_schema = "f142"
    stream_group_1["test_stream"] = test_stream_1

    stream_group_2 = StreamGroup("test_stream_group")
    test_stream_2 = EV42Stream("test_topic", "test_source")
    test_stream_2_schema = "ev42"
    stream_group_2["test_stream"] = test_stream_2

    component["test_stream_field_1"] = stream_group_1
    component["test_stream_field_2"] = stream_group_2
    flatbuffer = create_forwarder_config(model, "pva")

    info_from_buffer = deserialise_rf5k(flatbuffer)
    assert len(info_from_buffer.streams) == 2

    stream_info_1: StreamInfo = info_from_buffer.streams[0]
    stream_info_2: StreamInfo = info_from_buffer.streams[1]
    # Compare using sets because we don't know or care what order the stream are in
    assert {
        (stream_info_1.topic, stream_info_1.schema, stream_info_1.channel),
        (stream_info_2.topic, stream_info_2.schema, stream_info_2.channel),
    } == {
        (test_stream_1.topic, test_stream_1_schema, test_stream_1.source),
        (test_stream_2.topic, test_stream_2_schema, test_stream_2.source),
    }
