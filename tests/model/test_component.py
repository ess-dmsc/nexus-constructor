import numpy as np
from PySide2.QtGui import QVector3D

from nexus_constructor.model.component import TRANSFORMS_GROUP_NAME, Component
from nexus_constructor.model.module import Link, NS10Stream
from nexus_constructor.model.value_type import ValueTypes


def test_component_set_item_with_brackets_works_with_another_component():
    comp1 = Component("comp1")
    comp2 = Component("comp2")
    comp1[comp2.name] = comp2

    assert comp1[comp2.name] == comp2


def test_component_set_description_correctly_sets_description():
    comp = Component("comp3")
    description = "a component"
    comp.description = description

    assert comp.description == description


def test_component_set_field_with_numpy_array_correctly_sets_field_value():

    comp = Component("comp4")
    data = [[1], [2]]
    dtype = ValueTypes.INT
    field_name = "field1"
    field_value = np.asarray(data, dtype=int)

    comp.set_field_value(field_name, field_value, dtype)

    field_dataset = comp["field1"]
    assert field_dataset.name == field_name
    assert np.array_equal(field_dataset.values, field_value)
    assert field_dataset.type == dtype


def test_component_set_field_with_scalar_value_correctly_sets_field_value():
    comp = Component("comp4")
    field_name = "testfield"
    data = 123
    dtype = ValueTypes.INT

    comp.set_field_value(field_name, data, dtype)

    field_dataset = comp[field_name]

    assert field_dataset.name == field_name
    assert field_dataset.values == data
    assert field_dataset.type == dtype


def test_component_as_dict_contains_transformations():
    zeroth_transform_name = "test_transform_A"
    first_transform_name = "test_transform_B"
    test_component = Component(name="test_component")

    first_transform = test_component.add_translation(
        name=first_transform_name, vector=QVector3D(1, 0, 0)
    )
    zeroth_transform = test_component.add_translation(
        name=zeroth_transform_name,
        vector=QVector3D(0, 0, 1),
        depends_on=first_transform,
    )
    test_component.depends_on = zeroth_transform
    dictionary_output = test_component.as_dict([])

    assert dictionary_output["children"][0]["name"] == TRANSFORMS_GROUP_NAME
    child_names = [
        child["config"]["name"]
        for child in dictionary_output["children"][0]["children"]
    ]
    assert zeroth_transform_name in child_names
    assert first_transform_name in child_names


def test_component_as_dict_contains_stream_field():
    source = "PVS:pv1"
    topic = "topic1"
    name = "stream1"
    test_component = Component(name="test")
    test_component[name] = NS10Stream(parent_node=None, source=source, topic=topic)

    dictionary_output = test_component.as_dict([])

    assert dictionary_output["children"][0]["module"] == "ns10"
    assert dictionary_output["children"][0]["config"]["topic"] == topic
    assert dictionary_output["children"][0]["config"]["source"] == source


def test_component_as_dict_contains_links():
    name = "link1"
    target = "/entry/instrument/something"
    test_component = Component(name="test")
    test_component[name] = Link(parent_node=None, name=name, target=target)

    dictionary_output = test_component.as_dict([])

    assert dictionary_output["children"][0]["config"]["name"] == name
    assert dictionary_output["children"][0]["config"]["source"] == target
    assert dictionary_output["children"][0]["module"] == "link"
