import pytest

from nexus_constructor.model.stream import (
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
        SENVStream(source=source, topic=topic),
        TDCTStream(source=source, topic=topic),
        NS10Stream(source=source, topic=topic),
        EV42Stream(source=source, topic=topic),
    ],
)
def test_streams_with_name_source_and_topic(stream):
    stream_dict = stream.as_dict()["config"]
    assert stream_dict["topic"] == topic
    assert stream_dict["source"] == source


def test_f142_stream_optional_settings():
    type = "double"
    value_units = "m"
    array_size = "20"
    nexus_indices_index_every_kb = 3000
    nexus_indices_index_every_mb = 4000
    store_latest_into = 3
    stream = F142Stream(
        source=source,
        topic=topic,
        type=type,
        value_units=value_units,
        array_size=array_size,
        nexus_indices_index_every_kb=nexus_indices_index_every_kb,
        nexus_indices_index_every_mb=nexus_indices_index_every_mb,
        store_latest_into=store_latest_into,
    )
    stream_dict = stream.as_dict()["config"]
    assert stream_dict["topic"] == topic
    assert stream_dict["source"] == source
    assert stream_dict["dtype"] == type
    assert stream_dict["value_units"] == value_units
    assert stream_dict["array_size"] == array_size
    assert stream_dict["nexus.indices.index_every_kb"] == nexus_indices_index_every_kb
    assert stream_dict["nexus.indices.index_every_mb"] == nexus_indices_index_every_mb
    assert stream_dict["store_latest_into"] == store_latest_into


def test_ev42_stream_optional_settings():
    adc_pulse_debug = True
    nexus_chunk_chunk_kb = 1000
    nexus_chunk_chunk_mb = 2000
    nexus_indices_index_every_kb = 3000
    nexus_indices_index_every_mb = 4000
    stream = EV42Stream(
        topic=topic,
        source=source,
        adc_pulse_debug=adc_pulse_debug,
        nexus_chunk_chunk_kb=nexus_chunk_chunk_kb,
        nexus_chunk_chunk_mb=nexus_chunk_chunk_mb,
        nexus_indices_index_every_kb=nexus_indices_index_every_kb,
        nexus_indices_index_every_mb=nexus_indices_index_every_mb,
    )
    stream_dict = stream.as_dict()["config"]
    assert stream_dict["topic"] == topic
    assert stream_dict["source"] == source
    assert stream_dict["adc_pulse_debug"] == adc_pulse_debug
    assert stream_dict["nexus.indices.index_every_kb"] == nexus_indices_index_every_kb
    assert stream_dict["nexus.indices.index_every_mb"] == nexus_indices_index_every_mb
    assert stream_dict["nexus.chunk.chunk_kb"] == nexus_chunk_chunk_kb
    assert stream_dict["nexus.chunk.chunk_mb"] == nexus_chunk_chunk_mb
