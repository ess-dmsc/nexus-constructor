import json
from typing import Type

import pytest
from mock import mock_open, patch
from PySide6.QtGui import QVector3D

from nexus_constructor.common_attrs import NX_USER
from nexus_constructor.json.json_warnings import (
    JsonWarning,
    JsonWarningsContainer,
    TransformDependencyMissing,
)
from nexus_constructor.json.load_from_json import JSONReader
from nexus_constructor.json.load_from_json_utils import DEPENDS_ON_IGNORE
from nexus_constructor.model.component import Component
from nexus_constructor.model.module import Dataset
from nexus_constructor.model.value_type import ValueTypes


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
              "attributes":[{
                "name":"NX_class",
                "values":"NXinstrument"
              }],
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
            },
            {
              "module": "filewriter",
              "config": {
                "name": "start_time"
              }
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
                      "name":"transformations",
                      "type":"group",
                      "children":[
                        {
                          "module": "dataset",
                          "config": {
                              "name": "slit0",
                              "values": 10.0,
                              "type": "float"
                          },
                          "attributes": [
                            {
                                "name": "vector",
                                "dtype": "float",
                                "values": [
                                    0.0,
                                    0.0,
                                    1.0
                                ]
                            },
                            {
                                "name": "depends_on",
                                "dtype": "string",
                                "values": "."
                            },
                            {
                                "name": "transformation_type",
                                "dtype": "string",
                                "values": "translation"
                            },
                            {
                                "name": "units",
                                "dtype": "string",
                                "values": "metre"
                            }
                          ]
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
                  "type":"string",
                  "values":"NXsample"
                }
              ],
              "children":[
                {
                  "type":"group",
                  "name":"transformations",
                  "children":[]
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
                "name":"NX_class",
                "values":"NXinstrument"
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
        values=Dataset(
            parent_node=False, name="test", values=123, type=ValueTypes.DOUBLE
        ),
    )
    comp.depends_on = transformation
    return comp


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
    json_reader._load_from_json_dict(nexus_json_dictionary)

    assert json_reader.model.entry.children[1].name == sample_name


def test_GIVEN_component_with_name_WHEN_loading_from_json_THEN_new_model_contains_component_with_json_name(
    json_dict_with_component, json_reader
):
    component_name = "ComponentName"
    json_dict_with_component["children"][0]["children"][0]["children"][0][
        "name"
    ] = component_name
    node = json_reader._read_json_object(
        json_dict_with_component["children"][0]["children"][0]
    )

    assert node.children[0].name == component_name


def test_GIVEN_component_with_nx_class_WHEN_loading_from_json_THEN_new_model_contains_component_with_nx_class(
    json_dict_with_component, json_reader
):
    component_class = "NXcrystal"
    json_dict_with_component["children"][0]["children"][0]["children"][0]["attributes"][
        0
    ]["values"] = component_class
    node = json_reader._read_json_object(
        json_dict_with_component["children"][0]["children"][0]
    )
    assert node.children[0].nx_class == component_class


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


@pytest.mark.parametrize(
    "depends_on_path",
    [
        "/entry/instrument/componentname/transformations/slit0",
        "transformations/slit0",
        "slit0",
        ".",
        "",
        None
    ],
)
def test_GIVEN_json_with_component_depending_on_relative_transform_WHEN_loaded_THEN_model_updated(
    json_dict_with_component, json_reader, depends_on_path
):
    # Add depends_on dataset which points to a transformation in the JSON
    depends_on_dataset_str = f"""
    {{
      "module":"dataset",
      "attributes":[],
      "config":{{
        "type":"string",
        "values": "{depends_on_path}",
        "name":"depends_on"
      }}
    }}
    """
    depends_on_dataset = json.loads(depends_on_dataset_str)
    if depends_on_path is not None:
        transform_name = depends_on_path.split("/")[-1]
    else:
        transform_name = 'None'

    json_dict_with_component["children"][0]["children"][0]["children"][0][
        "children"
    ].append(depends_on_dataset)
    json_reader._load_from_json_dict(json_dict_with_component)
    if depends_on_path in DEPENDS_ON_IGNORE:
        try:
            json_reader._components_depends_on["componentname"][1].component_name
        except AttributeError:
            assert True
    else:
        assert (
            json_reader._components_depends_on["componentname"][1].component_name
            == "componentname"
        )
        assert (
            json_reader._components_depends_on["componentname"][1].transform_name == transform_name
        )


def test_when_experiment_id_in_json_then_it_is_added_to_entry(json_reader):
    json_string = """
   {
     "children": [
        {
           "name": "entry",
           "type": "group",
           "attributes": [
             {
                "name": "NX_class",
                "dtype": "string",
                "values": "NXentry"
             }
           ],
           "children": [
             {
                "module": "dataset",
                "config": {
                   "name": "experiment_identifier",
                   "dtype": "string",
                   "values": "ID_123456"
                }
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
        json_reader.load_model_from_json("filename")
        entry = json_reader.model.entry

    success = False
    for child in entry.children:
        try:
            if child.name == "experiment_identifier" and child.values == "ID_123456":
                success = True
                break
        except RuntimeError:
            pass
    assert success


def test_when_title_in_json_then_it_is_added_to_entry(json_reader):
    json_string = """
   {
     "children": [
        {
           "name": "entry",
           "type": "group",
           "attributes": [
             {
                "name": "NX_class",
                "dtype": "string",
                "values": "NXentry"
             }
           ],
           "children": [
             {
                "module": "dataset",
                "config": {
                   "name": "title",
                   "dtype": "string",
                   "values": "my title"
                }
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
        json_reader.load_model_from_json("filename")
        entry = json_reader.model.entry

    success = False
    for child in entry.children:
        try:
            if child.name == "title" and child.values == "my title":
                success = True
                break
        except RuntimeError:
            pass
    assert success


def test_when_users_are_in_json_then_they_are_added_to_entry(json_reader):
    user_john = {
        "name": "John Smith",
        "email": "js@ess.eu",
        "facility_user_id": "js90",
        "affiliation": "ESS",
    }

    user_betty = {
        "name": "Betty Boo",
        "email": "bb@doing.the.do",
        "facility_user_id": "bb70",
        "affiliation": "She Rockers",
    }

    json_string = """
        {
        "children": [
            {
                "name": "entry",
                "type": "group",
                "attributes": [
                    {"name": "NX_class", "dtype": "string", "values": "NXentry"}
                ],
                "children": [
                    {
                        "name": "user_JohnSmith",
                        "type": "group",
                        "attributes": [
                            {"name": "NX_class", "dtype": "string", "values": "NXuser"}
                        ],
                        "children": [
                            {
                                "module": "dataset",
                                "config": {
                                    "name": "name",
                                    "dtype": "string",
                                    "values": "%s"
                                }
                            },
                            {
                                "module": "dataset",
                                "config": {
                                    "name": "email",
                                    "dtype": "string",
                                    "values": "%s"
                                }
                            },
                            {
                                "module": "dataset",
                                "config": {
                                    "name": "facility_user_id",
                                    "dtype": "string",
                                    "values": "%s"
                                }
                            },
                            {
                                "module": "dataset",
                                "config": {
                                    "name": "affiliation",
                                    "dtype": "string",
                                    "values": "%s"
                                }
                            }
                        ]
                    },
                    {
                        "name": "user_BettyBoo",
                        "type": "group",
                        "attributes": [
                            {"name": "NX_class", "dtype": "string", "values": "NXuser"}
                        ],
                        "children": [
                            {
                                "module": "dataset",
                                "config": {
                                    "name": "name",
                                    "dtype": "string",
                                    "values": "%s"
                                }
                            },
                            {
                                "module": "dataset",
                                "config": {
                                    "name": "email",
                                    "dtype": "string",
                                    "values": "%s"
                                }
                            },
                            {
                                "module": "dataset",
                                "config": {
                                    "name": "facility_user_id",
                                    "dtype": "string",
                                    "values": "%s"
                                }
                            },
                            {
                                "module": "dataset",
                                "config": {
                                    "name": "affiliation",
                                    "dtype": "string",
                                    "values": "%s"
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """ % (
        user_john["name"],
        user_john["email"],
        user_john["facility_user_id"],
        user_john["affiliation"],
        user_betty["name"],
        user_betty["email"],
        user_betty["facility_user_id"],
        user_betty["affiliation"],
    )

    with patch(
        "nexus_constructor.json.load_from_json.open",
        mock_open(read_data=json_string),
        create=True,
    ):
        json_reader.load_model_from_json("filename")
        entry = json_reader.model.entry

    results = []
    for child in entry.children:
        try:
            if child.attributes[0].values == NX_USER:
                results.append({ds.name: ds.values for ds in child.children})
        except RuntimeError:
            pass

    assert user_john in results
    assert user_betty in results


def test_when_users_placeholder_in_json_then_entry_set(json_reader):
    json_string = """
        {
        "children": [
            {
                "name": "entry",
                "type": "group",
                "attributes": [
                    {"name": "NX_class", "dtype": "string", "values": "NXentry"}
                ],
                "children": [
                    "$USERS$"
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
        json_reader.load_model_from_json("filename")

    assert json_reader.model.entry.users_placeholder
