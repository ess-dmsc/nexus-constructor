import numpy as np
import pytest

from nexus_constructor.json.load_from_json_utils import _find_nx_class
from nexus_constructor.model.attributes import Attributes, FieldAttribute
from nexus_constructor.model.group import Group
from nexus_constructor.model.module import Dataset, Link
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP, ValueTypes


@pytest.mark.parametrize("class_attribute", [[{"name": "NX_class"}], [{"name": "123"}]])
def test_GIVEN_no_nx_class_values_for_component_WHEN_loading_from_json_THEN_json_loader_returns_false(
    class_attribute,
):
    assert not _find_nx_class(class_attribute)


@pytest.mark.parametrize(
    "class_attribute",
    [[{"name": "NX_class", "values": "NXmonitor"}], [{"NX_class": "NXmonitor"}]],
)
def test_GIVEN_nx_class_in_different_formats_WHEN_reading_class_information_THEN_read_nx_class_recognises_both_formats(
    class_attribute,
):

    assert _find_nx_class(class_attribute) == "NXmonitor"


def test_GIVEN_empty_dictionary_or_dictionary_with_no_attributes_WHEN_adding_attributes_THEN_returns_nothing():
    dataset = Dataset(parent_node=None, name="ds", values=123, type=ValueTypes.INT)
    assert not dataset.attributes


def test_GIVEN_dictionary_containing_attribute_WHEN_adding_attributes_THEN_attribute_object_is_created():
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


def test_GIVEN_dictionary_containing_attributes_WHEN_adding_attributes_THEN_attribute_objects_are_created():
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


def test_GIVEN_link_json_WHEN_adding_link_THEN_link_object_is_created():
    name = "link1"
    target = "/entry/instrument/detector1"
    link = Link(parent_node=None, name=name, source=target)
    assert link.name == name
    assert link.source == target
