import json

import pytest

from nexus_constructor.model.load_from_json import _contains_transformations


@pytest.fixture(scope="function")
def transformation_json():
    json_string = """
    {
      "type":"group",
      "name":"source",
      "children":[
        {
          "type":"dataset",
          "name":"depends_on",
          "dataset":{
            "type":"string"
          },
          "values":"/entry/instrument/source/transformations/location"
        },
        {
          "type":"dataset",
          "name":"name",
          "dataset":{
            "type":"string"
          },
          "values":"source"
        },
        {
          "type":"group",
          "name":"transformations",
          "children":[
            {
              "type":"dataset",
              "name":"location",
              "dataset":{
                "type":"double"
              },
              "values":0.0,
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
                },
                {
                  "name":"NX_class",
                  "values":"NXtransformation"
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
    """
    return json.loads(json_string)


@pytest.mark.parametrize("class_value", ["NXtransformation", "NXtransformations"])
def test_GIVEN_transformation_in_attributes_WHEN_checking_for_transformation_THEN_contains_transformations_returns_true(
    class_value, transformation_json
):
    transformations = transformation_json["children"][2]
    transformations["attributes"][0]["values"] = class_value
    assert _contains_transformations(transformations)


def test_GIVEN_no_transformation_class_in_attributes_WHEN_checking_for_transformations_THEN_contains_transformations_returns_false(
    transformation_json,
):
    transformations = transformation_json["children"][2]
    del transformations["attributes"][0]["name"]
    del transformations["attributes"][0]["values"]

    assert not _contains_transformations(transformations)
