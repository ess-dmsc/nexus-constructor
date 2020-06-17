import json

import pytest
from mock import patch, mock_open

from nexus_constructor.model.load_from_json import JSONReader, _retrieve_children_list


@pytest.fixture(scope="function")
def json_reader(template):
    return JSONReader(template)


@pytest.fixture(scope="function")
def nexus_json_dictionary():
    json_string = """
    {
      "nexus_structure": {
        "children": [
          {
            "name": "entry",
            "type": "group",
            "attributes": [
              {
                "name":  "NX_class",
                "values":  "NXentry"
              }
            ],
            "children": [
              {
                "name": "instrument",
                "type": "group",
                "attributes":
                  {
                    "NX_class":  "NXinstrument"
                  },
                "children": []
              },
              {
                "name": "sample",
                "type": "group",
                "attributes": [
                  {
                    "name":  "NX_class",
                    "values":  "NXsample"
                  }
                ],
                "children": [
                  {
                    "type": "group",
                    "name": "transformations",
                    "children": []
                  }
                ]
              }
            ]
          }
        ]
      }
    }
    """
    return json.loads(json_string)


def test_GIVEN_json_with_missing_value_WHEN_loading_from_json_THEN_json_loader_returns_false(json_reader):

    json_string = """
    {
      "nexus_structure": {
        "children": [
          {
            "name":,
            "type": "group",
            "attributes": [
              {
                "name":  "NX_class",
                "values":  "NXentry"
              }
            ],
            "children": [
              {
                "name": "instrument",
                "type": "group",
                "attributes":
                  {
                    "NX_class":  "NXinstrument"
                  },
                "children": []
              },
              {
                "name": "sample",
                "type": "group",
                "attributes": [
                  {
                    "name":  "NX_class",
                    "values":  "NXsample"
                  }
                ],
                "children": [
                  {
                    "type": "group",
                    "name": "transformations",
                    "children": []
                  }
                ]
              }
            ]
          }
        ]
      }
    }
    """

    with patch('nexus_constructor.model.load_from_json.open', mock_open(read_data=json_string), create=True):
        assert not json_reader.load_model_from_json("")


def test_GIVEN_unable_to_find_nexus_structure_field_WHEN_loading_from_json_THEN_json_loader_returns_false(json_reader):

    json_string = """
    {
      "crumpet": {
        "children": [
          {
            "name": "entry",
            "type": "group",
            "attributes": [
              {
                "name":  "NX_class",
                "values":  "NXentry"
              }
            ],
            "children": [
              {
                "name": "instrument",
                "type": "group",
                "attributes":
                  {
                    "NX_class":  "NXinstrument"
                  },
                "children": []
              },
              {
                "name": "sample",
                "type": "group",
                "attributes": [
                  {
                    "name":  "NX_class",
                    "values":  "NXsample"
                  }
                ],
                "children": [
                  {
                    "type": "group",
                    "name": "transformations",
                    "children": []
                  }
                ]
              }
            ]
          }
        ]
      }
    }
    """

    with patch('nexus_constructor.model.load_from_json.open', mock_open(read_data=json_string), create=True):
        assert not json_reader.load_model_from_json("")

    assert not _retrieve_children_list(json.loads(json_string))


def test_GIVEN_unable_to_find_first_children_field_WHEN_loading_from_json_THEN_json_loader_returns_false(json_reader):

    json_string = """
    {
      "nexus_structure": {
        "crumpet": [
          {
            "name": "entry",
            "type": "group",
            "attributes": [
              {
                "name":  "NX_class",
                "values":  "NXentry"
              }
            ],
            "children": [
              {
                "name": "instrument",
                "type": "group",
                "attributes":
                  {
                    "NX_class":  "NXinstrument"
                  },
                "children": []
              },
              {
                "name": "sample",
                "type": "group",
                "attributes": [
                  {
                    "name":  "NX_class",
                    "values":  "NXsample"
                  }
                ],
                "children": [
                  {
                    "type": "group",
                    "name": "transformations",
                    "children": []
                  }
                ]
              }
            ]
          }
        ]
      }
    }
    """

    with patch('nexus_constructor.model.load_from_json.open', mock_open(read_data=json_string), create=True):
        assert not json_reader.load_model_from_json("")

    assert not _retrieve_children_list(json.loads(json_string))


def test_GIVEN_unable_to_find_second_children_field_WHEN_loading_from_json_THEN_json_loader_returns_false(json_reader):

    json_string = """
    {
      "nexus_structure": {
        "children": [
          {
            "name": "entry",
            "type": "group",
            "attributes": [
              {
                "name":  "NX_class",
                "values":  "NXentry"
              }
            ],
            "crumpet": [
              {
                "name": "instrument",
                "type": "group",
                "attributes":
                  {
                    "NX_class":  "NXinstrument"
                  },
                "children": []
              },
              {
                "name": "sample",
                "type": "group",
                "attributes": [
                  {
                    "name":  "NX_class",
                    "values":  "NXsample"
                  }
                ],
                "children": [
                  {
                    "type": "group",
                    "name": "transformations",
                    "children": []
                  }
                ]
              }
            ]
          }
        ]
      }
    }
    """

    with patch('nexus_constructor.model.load_from_json.open', mock_open(read_data=json_string), create=True):
        assert not json_reader.load_model_from_json("")

    assert not _retrieve_children_list(json.loads(json_string))


def test_GIVEN_no_nx_class_for_component_WHEN_loading_from_json_THEN_json_loader_returns_false(json_reader):

    json_string = """
    {
      "nexus_structure": {
        "children": [
          {
            "name": "entry",
            "type": "group",
            "attributes": [
              {
                "name":  "NX_class",
                "values":  "NXentry"
              }
            ],
            "children": [
              {
                "name": "instrument",
                "type": "group",
                "attributes":
                  {
                    "NX_class":  "NXinstrument"
                  },
                "children": []
              },
              {
                "name": "sample",
                "type": "group",
                "attributes": [
                  {
                    "name":  "NX_class"
                  }
                ],
                "children": [
                  {
                    "type": "group",
                    "name": "transformations",
                    "children": []
                  }
                ]
              }
            ]
          }
        ]
      }
    }
    """

    with patch('nexus_constructor.model.load_from_json.open', mock_open(read_data=json_string), create=True):
        assert not json_reader.load_model_from_json("")
