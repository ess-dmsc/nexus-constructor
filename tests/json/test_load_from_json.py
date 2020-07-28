import json

import pytest
from mock import patch, mock_open

from nexus_constructor.json.load_from_json import JSONReader, _retrieve_children_list
from nexus_constructor.model.component import Component
from nexus_constructor.model.transformation import Transformation


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
                  "name":"componentname",
                  "type":"group",
                  "attributes":[
                    {
                      "name":"NX_class",
                      "type":"String",
                      "values":"NXaperture"
                    },
                    {
                      "name":"has_link",
                      "type":"String",
                      "values":false
                    }
                  ],
                  "children":[
                    {
                      "name":"description",
                      "type":"dataset",
                      "attributes":[
    
                      ]
                    },
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
                  "type":"String",
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
    transformation = Transformation(
        name="Transformation",
        type="Double",
        size="[1]",
        values="",
        parent_component=None,
    )
    return Component(name="Component", transforms_list=[transformation])


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


def test_GIVEN_transformation_with_matching_name_WHEN_finding_transformation_by_name_THEN_transformation_is_returned(
    json_reader, component_with_transformation
):
    transformation = component_with_transformation.transforms_list[0]
    assert transformation == json_reader._get_transformation_by_name(
        component_with_transformation, transformation.name, "DependentComponentName"
    )


def test_GIVEN_no_transformation_with_matching_name_WHEN_finding_transformation_by_name_THEN_warning_message_is_created(
    json_reader, component_with_transformation
):
    n_warnings = len(json_reader.warnings)

    transformation_name = component_with_transformation.transforms_list[0].name
    dependent_component_name = "DependentComponentName"

    component_with_transformation.transforms_list.clear()
    assert (
        json_reader._get_transformation_by_name(
            component_with_transformation, transformation_name, dependent_component_name
        )
        is None
    )
    assert len(json_reader.warnings) == n_warnings + 1
    assert all(
        [
            expected_text in json_reader.warnings[-1]
            for expected_text in [
                component_with_transformation.name,
                transformation_name,
                dependent_component_name,
            ]
        ]
    )
