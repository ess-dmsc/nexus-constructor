import json

import pytest
from mock import Mock

from nexus_constructor.model.component import Component
from nexus_constructor.model.load_from_json import (
    _contains_transformations,
    TransformationReader,
)


@pytest.fixture(scope="function")
def transformation_json():
    json_string = """
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
    """
    return json.loads(json_string)


@pytest.fixture(scope="function")
def attributes_list(transformation_json):
    return transformation_json["children"][0]["attributes"]


@pytest.fixture(scope="function")
def transformation_reader(transformation_json):
    parent_component = Mock(spec=Component)
    parent_component.name = "ParentComponentName"
    parent_component.transforms_list = []
    entry = [transformation_json]
    return TransformationReader(parent_component, entry)


@pytest.mark.parametrize("class_value", ["NXtransformation", "NXtransformations"])
def test_GIVEN_transformation_in_attributes_WHEN_checking_for_transformation_THEN_contains_transformations_returns_true(
    class_value, transformation_json
):
    transformation_json["attributes"][0]["values"] = class_value
    assert _contains_transformations(transformation_json)


def test_GIVEN_no_transformation_class_in_attributes_WHEN_checking_for_transformations_THEN_contains_transformations_returns_false(
    transformation_json,
):
    del transformation_json["attributes"][0]["name"]
    del transformation_json["attributes"][0]["values"]

    assert not _contains_transformations(transformation_json)


def test_GIVEN_no_attributes_field_in_dict_WHEN_checking_for_transformations_THEN_contains_transformations_returns_false(
    transformation_json,
):
    del transformation_json["attributes"]
    assert not _contains_transformations(transformation_json)


def test_GIVEN_property_not_found_WHEN_looking_for_transformation_property_THEN_get_transformation_property_returns_failure_value(
    transformation_json, transformation_reader
):
    n_warnings = len(transformation_reader.warnings)

    failure_value = 20
    property_name = "DoesNotExist"
    property_value = transformation_reader._get_transformation_property(
        property_name, transformation_json["children"][0], failure_value
    )

    # Check that the failure value was returned
    assert property_value == failure_value
    # Check that the number of warnings has increased
    assert len(transformation_reader.warnings) == n_warnings + 1
    # Check that the latest warning mentions the name of the property that could not be found
    assert property_name in transformation_reader.warnings[-1]


def test_GIVEN_property_is_found_WHEN_looking_for_transformation_property_THEN_get_transformation_property_returns_property_value(
    transformation_json, transformation_reader
):
    n_warnings = len(transformation_reader.warnings)

    # Set the values property
    transformation_json["children"][0]["values"] = json_value = 300

    property_value = transformation_reader._get_transformation_property(
        "values", transformation_json["children"][0], failure_value=50
    )

    # Check that the json value was returned
    assert property_value == json_value
    # Check that the number of warnings has remained the same
    assert len(transformation_reader.warnings) == n_warnings


def test_GIVEN_property_is_in_list_WHEN_looking_for_transformation_property_THEN_get_property_in_list_returns_true(
    transformation_reader, attributes_list
):
    n_warnings = len(transformation_reader.warnings)

    # Set the units value
    attributes_list[0]["values"] = json_value = "cm"

    property_value = transformation_reader._find_property_in_list(
        "units", "TransformationName", attributes_list, failure_value="yards"
    )

    # Check that the json value was returned
    assert property_value == json_value
    # Check that the number of warnings has remained the same
    assert len(transformation_reader.warnings) == n_warnings


def test_GIVEN_property_name_not_in_list_WHEN_looking_for_transformation_property_THEN_get_property_in_list_returns_false(
    transformation_reader, attributes_list
):
    n_warnings = len(transformation_reader.warnings)
    failure_value = "yards"

    # Remove the name field from the nested units dictionary
    del attributes_list[0]["name"]

    property_value = transformation_reader._find_property_in_list(
        "units", "TransformationName", attributes_list, failure_value
    )

    # Check that the failure value was returned
    assert property_value == failure_value
    # Check that the number of warnings has increased
    assert len(transformation_reader.warnings) == n_warnings + 1
    # Check that the latest warning mentions the name of the property that could not be found
    assert "units" in transformation_reader.warnings[-1]


def test_GIVEN_property_value_not_in_list_WHEN_looking_for_transformation_property_THEN_get_property_in_list_returns_false(
    transformation_reader, attributes_list
):
    n_warnings = len(transformation_reader.warnings)
    failure_value = "yards"

    # Remove the values field from the nested units dictionary
    del attributes_list[0]["values"]

    property_value = transformation_reader._find_property_in_list(
        "units", "TransformationName", attributes_list, failure_value
    )

    # Check that the failure value was returned
    assert property_value == failure_value
    # Check that the number of warnings has increased
    assert len(transformation_reader.warnings) == n_warnings + 1
    # Check that the latest warning mentions the name of the property that could not be found
    assert "units" in transformation_reader.warnings[-1]


def test_GIVEN_no_attributes_WHEN_attempting_to_create_transformations_THEN_transformations_are_not_created(
    transformation_reader, transformation_json
):
    del transformation_json["children"][0]["attributes"]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_transformation_type_WHEN_attempting_to_create_transformations_THEN_transformations_are_not_created(
    transformation_reader, transformation_json
):
    # Delete the transformation type nested dictionary
    del transformation_json["children"][0]["attributes"][1]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_units_WHEN_attempting_to_create_transformations_THEN_transformations_are_not_created(
    transformation_reader, transformation_json
):
    # Delete the units nested dictionary
    del transformation_json["children"][0]["attributes"][0]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_all_information_present_WHEN_attempting_to_create_transformations_THEN_transformation_is_created(
    transformation_reader, transformation_json
):
    transformation_reader._create_transformations(transformation_json["children"])
    transformation_reader.parent_component._create_and_add_transform.assert_called()
