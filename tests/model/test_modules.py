import numpy as np
import pytest

from nexus_constructor.model.attributes import Attributes, FieldAttribute
from nexus_constructor.model.group import Group
from nexus_constructor.model.module import (
    Dataset,
    EV42Stream,
    F142Stream,
    Link,
    NS10Stream,
    SENVStream,
    TDCTStream,
)
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP, ValueTypes

topic = "topic1"
source = "source1"
name = "stream1"


def test_dataset_as_dict_contains_expected_keys():
    input_name = "test_dataset"
    test_dataset = Dataset(
        parent_node=None, name=input_name, type=ValueTypes.STRING, values="the_value"
    )
    dictionary_output = test_dataset.as_dict([])
    for expected_key in ("module", "config"):
        assert expected_key in dictionary_output.keys()

    assert dictionary_output["config"]["name"] == input_name


def test_GIVEN_empty_attributes_WHEN_adding_attributes_THEN_returns_nothing():
    dataset = Dataset(parent_node=None, name="ds", values=123, type=ValueTypes.INT)
    assert not dataset.attributes


def test_GIVEN_attribute_info_WHEN_adding_attributes_THEN_attribute_object_is_created():
    key = "units"
    value = "m"
    dataset = Dataset(parent_node=None, name="ds", values=123, type=ValueTypes.INT)
    attributes = Attributes()
    attributes.set_attribute_value(key, value)
    dataset.attributes = attributes
    assert len(dataset.attributes) == 1
    assert isinstance(dataset.attributes[0], FieldAttribute)
    assert dataset.attributes[0].name == key
    assert dataset.attributes[0].values == value


def test_GIVEN_attributes_info_WHEN_adding_attributes_THEN_attribute_objects_are_created():
    key1 = "units"
    val1 = "m"
    key2 = "testkey"
    val2 = "testval"
    dataset = Dataset(parent_node=None, name="ds", values=123, type=ValueTypes.INT)
    attributes = Attributes()
    attributes.set_attribute_value(key1, val1)
    attributes.set_attribute_value(key2, val2)
    dataset.attributes = attributes
    assert len(dataset.attributes) == 2
    assert dataset.attributes[0].name == key1
    assert dataset.attributes[0].values == val1
    assert dataset.attributes[1].name == key2
    assert dataset.attributes[1].values == val2


def test_GIVEN_dataset_with_string_value_WHEN_adding_dataset_THEN_dataset_object_is_created_with_correct_dtype():
    name = "description"
    values = "a description"
    parent = Group(name="test")
    ds = Dataset(parent_node=parent, type=ValueTypes.STRING, values=values, name=name)
    assert ds.name == name
    assert ds.values == values
    assert ds.parent_node == parent
    assert ds.type == ValueTypes.STRING


def test_GIVEN_dataset_with_array_value_WHEN_adding_dataset_THEN_dataset_object_is_created_with_numpy_array_as_value():
    name = "an_array"
    values = [1.1, 2.2, 3.3, 4.4]
    dtype = ValueTypes.FLOAT

    np_array = np.array(values, dtype=VALUE_TYPE_TO_NP[dtype])
    parent = Group(name="test")
    ds = Dataset(parent_node=parent, type=dtype, values=np_array, name=name)

    assert ds.name == name
    assert np.array_equal(ds.values, np_array)
    assert ds.parent_node == parent
    assert ds.type == dtype


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


def test_GIVEN_link_info_WHEN_adding_link_THEN_link_object_is_created():
    name = "link1"
    target = "/entry/instrument/detector1"
    link = Link(parent_node=None, name=name, target=target)
    assert link.name == name
    assert link.target == target
