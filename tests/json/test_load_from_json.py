import json
from typing import Type

import numpy as np
import pytest
from mock import mock_open, patch
from PySide2.QtGui import QVector3D

from nexus_constructor.json.json_warnings import (
    JsonWarning,
    JsonWarningsContainer,
    TransformDependencyMissing,
)
from nexus_constructor.json.load_from_json import (
    JSONReader,
    _add_attributes,
    _create_dataset,
    _create_link,
    _retrieve_children_list,
)
from nexus_constructor.model.attributes import FieldAttribute
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.group import Group
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP, ValueTypes


@pytest.fixture(scope="function")
def json_reader() -> JSONReader:
    return JSONReader()


@pytest.fixture(scope="function")
def nexus_json_dictionary() -> dict:
    json_string = """
    {
      "children":[
        {
          "name":"entry",
          "type":"group",
          "attributes":[
            {
              "name":"NX_class",
              "values":"NXentry"
            }
          ],
          "children":[
            {
              "name":"instrument",
              "type":"group",
              "attributes":{
                "NX_class":"NXinstrument"
              },
              "children":[
    
              ]
            },
            {
              "name":"sample",
              "type":"group",
              "attributes":[
                {
                  "name":"NX_class",
                  "values":"NXsample"
                }
              ],
              "children":[
                {
                  "type":"group",
                  "name":"transformations",
                  "children":[
    
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
    """
    return json.loads(json_string)


@pytest.fixture(scope="function")
def json_dict_with_component():
    json_string = """
    {
      "children":[
        {
          "name":"entry",
          "type":"group",
          "attributes":[
            {
              "name":"NX_class",
              "type":"string",
              "values":"NXentry"
            }
          ],
          "children":[
            {
              "name":"instrument",
              "type":"group",
              "attributes":[
                {
                  "name":"NX_class",
                  "type":"string",
                  "values":"NXinstrument"
                }
              ],
              "children":[
                {
                  "name":"componentname",
                  "type":"group",
                  "attributes":[
                    {
                      "name":"NX_class",
                      "type":"string",
                      "values":"NXaperture"
                    }
                  ],
                  "children":[
                    {
                      "type":"group",
                      "name":"transformations",
                      "children":[
    
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "name":"sample",
              "type":"group",
              "attributes":[
                {
                  "name":"NX_class",
                  "type":"string",
                  "values":"NXsample"
                }
              ],
              "children":[
                {
                  "type":"group",
                  "name":"transformations",
                  "children":[
    
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
    """
    return json.loads(json_string)


@pytest.fixture(scope="function")
def json_dict_with_component_and_transform():
    json_string = """
    {
      "children":[
        {
          "name":"entry",
          "type":"group",
          "attributes":[
            {
              "name":"NX_class",
              "type":"String",
              "values":"NXentry"
            }
          ],
          "children":[
            {
              "name":"instrument",
              "type":"group",
              "attributes":[
                {
                  "name":"NX_class",
                  "type":"String",
                  "values":"NXinstrument"
                }
              ],
              "children":[
                {
                  "name":"test_component",
                  "type":"group",
                  "attributes":[
                    {
                      "name":"NX_class",
                      "type":"String",
                      "values":"NXaperture"
                    }
                  ],
                  "children":[
                    {
                      "module":"dataset",
                      "attributes":[],
                      "config":{
                        "name":"depends_on",
                        "type":"string",
                        "values": "/entry/instrument/test_component/transformations/location"
                      }
                    },
                    {
                      "type":"group",
                      "name":"transformations",
                      "children":[
                        {
                          "module":"dataset",
                          "config":{
                            "type":"double",
                            "values":1.0,
                            "name":"location"
                          },
                          "attributes":[
                            {
                              "name":"units",
                              "values":"m"
                            },
                            {
                              "name":"transformation_type",
                              "values":"translation"
                            },
                            {
                              "name":"vector",
                              "values":[
                                0.0,
                                0.0,
                                0.0
                              ],
                              "type":"double"
                            },
                            {
                              "name":"depends_on",
                              "values":"."
                            }
                          ]
                        }
                      ],
                      "attributes":[
                        {
                          "name":"NX_class",
                          "values":"NXtransformations"
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "name":"sample",
              "type":"group",
              "attributes":[
                {
                  "name":"NX_class",
                  "type":"String",
                  "values":"NXsample"
                }
              ]
            }
          ]
        }
      ]
    }
    """
    return json.loads(json_string)


def test_GIVEN_json_with_missing_value_WHEN_loading_from_json_THEN_json_loader_returns_false(
    json_reader,
):
    json_string = """
    {
      "children":[
        {
          "name":,
          "type":"group",
          "attributes":[
            {
              "name":"NX_class",
              "values":"NXentry"
            }
          ],
          "children":[
            {
              "name":"instrument",
              "type":"group",
              "attributes":{
                "NX_class":"NXinstrument"
              },
              "children":[
    
              ]
            },
            {
              "name":"sample",
              "type":"group",
              "attributes":[
                {
                  "name":"NX_class",
                  "values":"NXsample"
                }
              ],
              "children":[
                {
                  "type":"group",
                  "name":"transformations",
                  "children":[
    
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
    """

    with patch(
        "nexus_constructor.json.load_from_json.open",
        mock_open(read_data=json_string),
        create=True,
    ):
        assert not json_reader.load_model_from_json("filename")


@pytest.fixture(scope="function")
def component_with_transformation() -> Component:
    comp = Component(name="Component")
    transformation = comp.add_rotation(
        name="Transformation",
        angle=90,
        axis=QVector3D(1, 0, 0),
        depends_on=None,
        values=Dataset(name="test", values=123, type=ValueTypes.DOUBLE),
    )
    comp.depends_on = transformation
    return comp


def test_GIVEN_unable_to_find_nexus_structure_field_WHEN_loading_from_json_THEN_json_loader_returns_false():
    assert not _retrieve_children_list(dict())


def test_GIVEN_unable_to_find_first_children_field_WHEN_loading_from_json_THEN_json_loader_returns_false():
    assert not _retrieve_children_list({"": None})


def test_GIVEN_unable_to_find_second_children_field_WHEN_loading_from_json_THEN_json_loader_returns_false():
    assert not _retrieve_children_list({"children": [dict()]})


@pytest.mark.parametrize("nx_class", ["", "notannxclass"])
def test_GIVEN_invalid_nx_class_WHEN_obtained_nx_class_value_THEN_validate_nx_class_returns_false(
    nx_class, json_reader
):
    assert not json_reader._validate_nx_class("name", nx_class)


def test_GIVEN_json_with_sample_WHEN_loading_from_json_THEN_new_model_contains_new_sample_name(
    nexus_json_dictionary, json_reader
):
    sample_name = "NewSampleName"
    nexus_json_dictionary["children"][0]["children"][1]["name"] = sample_name

    children_list = _retrieve_children_list(nexus_json_dictionary)

    for child in children_list:
        json_reader._read_json_object(child)

    assert json_reader.entry.instrument.sample.name == sample_name


def test_GIVEN_no_nx_instrument_class_WHEN_loading_from_json_THEN_read_json_object_returns_false(
    nexus_json_dictionary, json_reader
):
    nx_instrument = nexus_json_dictionary["children"][0]["children"][0]
    nx_instrument["attributes"]["NX_class"] = None

    assert not json_reader._read_json_object(nx_instrument)


def test_GIVEN_component_with_name_WHEN_loading_from_json_THEN_new_model_contains_component_with_json_name(
    json_dict_with_component, json_reader
):
    component_name = "ComponentName"
    json_dict_with_component["children"][0]["children"][0]["children"][0][
        "name"
    ] = component_name
    json_reader._read_json_object(
        json_dict_with_component["children"][0]["children"][0]
    )

    assert json_reader.entry.instrument.component_list[1].name == component_name


def test_GIVEN_component_with_nx_class_WHEN_loading_from_json_THEN_new_model_contains_component_with_nx_class(
    json_dict_with_component, json_reader
):
    component_class = "NXcrystal"
    json_dict_with_component["children"][0]["children"][0]["children"][0]["attributes"][
        0
    ]["values"] = component_class
    json_reader._read_json_object(
        json_dict_with_component["children"][0]["children"][0]
    )

    assert json_reader.entry.instrument.component_list[1].nx_class == component_class


def test_GIVEN_json_with_component_depending_on_transform_WHEN_loaded_THEN_component_in_model_contains_transform(
    json_dict_with_component_and_transform, json_reader
):
    json_reader._load_from_json_dict(json_dict_with_component_and_transform)
    component_found = False
    for component in json_reader.entry.instrument.component_list:
        if component.name == "test_component":
            component_found = True
            assert len(component.transforms) == 1
            assert component.transforms[0].name == "location"
    assert component_found


def contains_warning_of_type(
    json_warnings: JsonWarningsContainer, warning_type: Type[JsonWarning]
) -> bool:
    return any(isinstance(json_warning, warning_type) for json_warning in json_warnings)


def test_GIVEN_json_with_component_depending_on_non_existent_transform_WHEN_loaded_THEN_warning_is_added(
    json_dict_with_component, json_reader
):
    depends_on_dataset_str = """
    {
      "module":"dataset",
      "attributes":[],
      "config":{
        "type":"string",
        "values": "/entry/instrument/test_component/transformations/location",
        "name":"depends_on"
      }
    }
    """
    depends_on_dataset = json.loads(depends_on_dataset_str)

    # Add depends_on dataset which points to a transformation which does not exist in the JSON
    json_dict_with_component["children"][0]["children"][0]["children"][0][
        "children"
    ].append(depends_on_dataset)
    json_reader._load_from_json_dict(json_dict_with_component)

    assert contains_warning_of_type(json_reader.warnings, TransformDependencyMissing)


def test_GIVEN_json_with_transformation_depending_on_non_existent_transform_WHEN_loaded_THEN_warning_is_added(
    json_dict_with_component_and_transform, json_reader
):
    # Makes depends_on attribute of transformation point to a transformation which does not exist
    for node in json_dict_with_component_and_transform["children"][0]["children"][0][
        "children"
    ][0]["children"]:
        if "name" in node and node["name"] == "transformations":
            for attribute in node["children"][0]["attributes"]:
                if attribute["name"] == "depends_on":
                    attribute["values"] = "/transform/does/not/exist"

    json_reader._load_from_json_dict(json_dict_with_component_and_transform)

    assert contains_warning_of_type(
        json_reader.warnings, TransformDependencyMissing
    ), "Expected a warning due to depends_on pointing to a non-existent transform"


@pytest.mark.parametrize(
    "test_input",
    (
        {},
        {
            "module": "dataset",
            "config": {"values": 0},
        },
        {"attributes": []},
    ),  # noqa E231
)
def test_GIVEN_empty_dictionary_or_dictionary_with_no_attributes_WHEN_adding_attributes_THEN_returns_nothing(
    test_input,
):
    dataset = Dataset(name="ds", values=123, type=ValueTypes.INT)
    _add_attributes(test_input, dataset)
    assert not dataset.attributes


def test_GIVEN_dictionary_containing_attribute_WHEN_adding_attributes_THEN_attribute_object_is_created():
    key = "units"
    value = "m"
    test_dict = {"attributes": [{"name": key, "values": value}]}
    dataset = Dataset(name="ds", values=123, type=ValueTypes.INT)
    _add_attributes(test_dict, dataset)
    assert len(dataset.attributes) == 1
    assert isinstance(dataset.attributes[0], FieldAttribute)
    assert dataset.attributes[0].name == key
    assert dataset.attributes[0].values == value


def test_GIVEN_dictionary_containing_attributes_WHEN_adding_attributes_THEN_attribute_objects_are_created():
    key1 = "units"
    val1 = "m"
    key2 = "testkey"
    val2 = "testval"
    test_dict = {
        "attributes": [{"name": key1, "values": val1}, {"name": key2, "values": val2}]
    }
    dataset = Dataset(name="ds", values=123, type=ValueTypes.INT)
    _add_attributes(test_dict, dataset)
    assert len(dataset.attributes) == 2
    assert dataset.attributes[0].name == key1
    assert dataset.attributes[0].values == val1
    assert dataset.attributes[1].name == key2
    assert dataset.attributes[1].values == val2


def test_GIVEN_link_json_WHEN_adding_link_THEN_link_object_is_created():
    name = "link1"
    target = "/entry/instrument/detector1"
    test_dict = {"name": name, "target": target}
    link = _create_link(test_dict)
    assert link.name == name
    assert link.target == target


def test_GIVEN_dataset_with_string_value_WHEN_adding_dataset_THEN_dataset_object_is_created_with_correct_dtype():
    name = "description"
    values = "a description"
    parent = Group(name="test")
    test_dict = {
        "module": "dataset",
        "config": {"type": ValueTypes.STRING, "values": values, "name": name},
    }

    ds = _create_dataset(test_dict, parent)

    assert ds.name == name
    assert ds.values == values
    assert ds.parent_node == parent
    assert ds.type == ValueTypes.STRING


def test_GIVEN_dataset_with_array_value_WHEN_adding_dataset_THEN_dataset_object_is_created_with_numpy_array_as_value():
    name = "an_array"
    values = [1.1, 2.2, 3.3, 4.4]
    dtype = ValueTypes.FLOAT

    np_array = np.array(values, dtype=VALUE_TYPE_TO_NP[dtype])

    test_dict = {
        "module": "dataset",
        "config": {"type": dtype, "values": values, "name": name},
    }
    parent = Group(name="test")
    ds = _create_dataset(test_dict, parent)

    assert ds.name == name
    assert np.array_equal(ds.values, np_array)
    assert ds.parent_node == parent
    assert ds.type == dtype
