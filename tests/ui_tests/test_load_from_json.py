import pytest
from mock import patch, mock_open

from nexus_constructor.model.load_from_json import JSONReader


@pytest.fixture(scope="function")
def json_reader(template):
    return JSONReader(template)


def test_GIVEN_invalid_json_WHEN_loading_from_json_THEN_json_loader_returns_false(json_reader):

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
                "attributes": [
                  {
                    "name":  "NX_class",
                    "values":  "NXinstrument"
                  }
                ],
                "children": []
              },
              {
                "name": "wedgie",
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
        assert not json_reader.load_model_from_json("filename")
