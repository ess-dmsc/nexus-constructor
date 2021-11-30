import pytest

from nexus_constructor.model.module import (
    EV42Stream,
    F142Stream,
    NS10Stream,
    SENVStream,
    TDCTStream,
)

topic = "topic1"
source = "source1"
name = "stream1"


@pytest.mark.parametrize(
    "stream",
    [
        SENVStream(parent_node=None, source=source, topic=topic),
        TDCTStream(parent_node=None, source=source, topic=topic),
        NS10Stream(parent_node=None, source=source, topic=topic),
        EV42Stream(parent_node=None, source=source, topic=topic),
    ],
)
def test_streams_with_name_source_and_topic(stream):
    stream_dict = stream.as_dict([])["config"]
    assert stream_dict["topic"] == topic
    assert stream_dict["source"] == source


def test_f142_stream_optional_settings():
    type = "double"
    value_units = "m"
    array_size = "20"
    chunk_size = 1000
    cue_interval = 5
    stream = F142Stream(
        parent_node=None,
        source=source,
        topic=topic,
        type=type,
        value_units=value_units,
        array_size=array_size,
    )
    stream.cue_interval = cue_interval
    stream.chunk_size = chunk_size
    stream_dict = stream.as_dict([])["config"]
    assert stream_dict["topic"] == topic
    assert stream_dict["source"] == source
    assert stream_dict["dtype"] == type
    assert stream_dict["value_units"] == value_units
    assert stream_dict["array_size"] == array_size


def test_ev42_stream_optional_settings():
    adc_pulse_debug = True
    chunk_size = 1000
    cue_interval = 5
    stream = EV42Stream(
        parent_node=None,
        topic=topic,
        source=source,
    )
    stream.adc_pulse_debug = adc_pulse_debug
    stream.cue_interval = cue_interval
    stream.chunk_size = chunk_size
    stream_dict = stream.as_dict([])["config"]
    assert stream_dict["topic"] == topic
    assert stream_dict["source"] == source
    assert stream_dict["adc_pulse_debug"] == adc_pulse_debug
    assert stream_dict["chunk_size"] == chunk_size
    assert stream_dict["cue_interval"] == cue_interval
