import json
from typing import Dict, Tuple

import pytest
from mock import Mock
from PySide6.QtGui import QVector3D

from nexus_constructor.json.transform_id import TransformId
from nexus_constructor.json.transformation_reader import (
    TRANSFORMATION_MAP,
    TransformationReader,
    _create_transformation_dataset,
    _create_transformation_datastream_group,
    _is_transformation_group,
)
from nexus_constructor.model.component import Component
from nexus_constructor.model.transformation import Transformation


@pytest.fixture(scope="function")
def transformation_json():
    json_string = """
    {
      "type":"group",
      "name":"transformations",
      "children":[
        {
          "module":"dataset",
          "config":{
            "name":"location",
            "type":"double",
            "values":0.0
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
    """
    return json.loads(json_string)


@pytest.fixture(scope="function")
def transformation_with_stream_json():
    json_string = """
    {
      "type": "group",
      "name": "transformations",
      "children": [
          {
            "module": "f142",
            "config": {
            "source": ":: SOURCE ::",
            "topic": ":: TOPIC ::",
            "dtype": "double",
            "value_units": "m",
            "name": "location"
            },
          "attributes": [
              {
                "name": "transformation_type",
                "dtype": "string",
                "values": "Translation"
              },
              {
                "name": "units",
                "dtype": "string",
                "values": "m"
              },
              {
                "name": "vector",
                "dtype": "string",
                "values": [
                  0.0,
                  0.0,
                  1.0
                ]
              }
            ]
          }
        ],
        "attributes": [
          {
            "name": "NX_class",
            "values": "NXtransformations"
          }
      ]
    }"""
    return json.loads(json_string)


@pytest.fixture(scope="function")
def attributes_list(transformation_json):
    return transformation_json["children"][0]["attributes"]


PARENT_COMPONENT_NAME = "ParentComponentName"


@pytest.fixture(scope="function")
def transformation_reader(transformation_json):
    parent_component = Mock(spec=Component)
    parent_component.name = PARENT_COMPONENT_NAME
    parent_component.absolute_path = "/entry/" + parent_component.name
    entry = [transformation_json]
    transforms_with_dependencies: Dict[
        TransformId, Tuple[Transformation, TransformId]
    ] = {}
    return TransformationReader(parent_component, entry, transforms_with_dependencies)


def test_GIVEN_nxtransformation_in_attributes_WHEN_checking_for_transformations_THEN_contains_transformations_returns_true(
    transformation_json,
):
    transformation_json["attributes"][0]["values"] = "NXtransformations"
    assert _is_transformation_group(transformation_json)


def test_GIVEN_no_nxtransformation_in_attributes_WHEN_checking_for_transformations_THEN_contains_transformations_returns_false(
    transformation_json,
):
    transformation_json["attributes"][0]["values"] = "NXsomething"
    assert not _is_transformation_group(transformation_json)


def test_GIVEN_no_transformation_class_in_attributes_WHEN_checking_for_transformations_THEN_contains_transformations_returns_false(
    transformation_json,
):
    del transformation_json["attributes"][0]["name"]
    del transformation_json["attributes"][0]["values"]

    assert not _is_transformation_group(transformation_json)


def test_GIVEN_no_attributes_field_in_dict_WHEN_checking_for_transformations_THEN_contains_transformations_returns_false(
    transformation_json,
):
    del transformation_json["attributes"]
    assert not _is_transformation_group(transformation_json)


def test_GIVEN_attribute_not_found_WHEN_looking_for_transformation_attribute_THEN_get_transformation_attribute_returns_failure_value(
    transformation_json, transformation_reader
):
    n_warnings = len(transformation_reader.warnings)

    failure_value = 20
    attribute_name = "DoesNotExist"
    attribute_value = transformation_reader._get_transformation_attribute(
        attribute_name, transformation_json["children"][0], failure_value=failure_value
    )

    # Check that the failure value was returned
    assert attribute_value == failure_value
    # Check that the number of warnings has increased
    assert len(transformation_reader.warnings) == n_warnings + 1
    # Check that the latest warning mentions the name of the attribute that could not be found
    assert attribute_name in transformation_reader.warnings[-1].message


def test_GIVEN_attribute_is_found_WHEN_looking_for_transformation_attribute_THEN_get_transformation_attribute_returns_attribute_value(
    transformation_json, transformation_reader
):
    n_warnings = len(transformation_reader.warnings)

    # Set the values attribute
    transformation_json["children"][0]["values"] = json_value = 300

    attribute_value = transformation_reader._get_transformation_attribute(
        "values", transformation_json["children"][0], failure_value=50
    )

    # Check that the json value was returned
    assert attribute_value == json_value
    # Check that the number of warnings has remained the same
    assert len(transformation_reader.warnings) == n_warnings


def test_GIVEN_attribute_is_in_list_WHEN_looking_for_transformation_attribute_THEN_get_attribute_in_list_returns_true(
    transformation_reader, attributes_list
):
    n_warnings = len(transformation_reader.warnings)

    # Set the units value
    attributes_list[0]["values"] = json_value = "cm"

    attribute_value = transformation_reader._find_attribute_in_list(
        "units", "TransformationName", attributes_list, failure_value="yards"
    )

    # Check that the json value was returned
    assert attribute_value == json_value
    # Check that the number of warnings has remained the same
    assert len(transformation_reader.warnings) == n_warnings


def test_GIVEN_attribute_name_not_in_list_WHEN_looking_for_transformation_attribute_THEN_get_attribute_in_list_returns_false(
    transformation_reader, attributes_list
):
    n_warnings = len(transformation_reader.warnings)
    failure_value = "yards"

    # Remove the name field from the nested units dictionary
    del attributes_list[0]["name"]

    attribute_value = transformation_reader._find_attribute_in_list(
        "units", "TransformationName", attributes_list, failure_value
    )

    # Check that the failure value was returned
    assert attribute_value == failure_value
    # Check that the number of warnings has increased
    assert len(transformation_reader.warnings) == n_warnings + 1
    # Check that the latest warning mentions the name of the attribute that could not be found
    assert "units" in transformation_reader.warnings[-1].message


def test_GIVEN_attribute_value_not_in_list_WHEN_looking_for_transformation_attribute_THEN_get_attribute_in_list_returns_false(
    transformation_reader, attributes_list
):
    n_warnings = len(transformation_reader.warnings)
    failure_value = "yards"

    # Remove the values field from the nested units dictionary
    del attributes_list[0]["values"]

    attribute_value = transformation_reader._find_attribute_in_list(
        "units", "TransformationName", attributes_list, failure_value
    )

    # Check that the failure value was returned
    assert attribute_value == failure_value
    # Check that the number of warnings has increased
    assert len(transformation_reader.warnings) == n_warnings + 1
    # Check that the latest warning mentions the name of the attribute that could not be found
    assert "units" in transformation_reader.warnings[-1].message


def test_GIVEN_no_values_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    del transformation_json["children"][0]["config"]["values"]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_no_transformation_without_config(transformation_reader, transformation_json):
    del transformation_json["children"][0]["config"]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_datatype_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    transformation_json["children"][0]["config"]["a"] = "b"
    del transformation_json["children"][0]["config"]["type"]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_attributes_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    del transformation_json["children"][0]["attributes"]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_transformation_type_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    # Delete the transformation type nested dictionary
    del transformation_json["children"][0]["attributes"][1]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_units_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    # Delete the units nested dictionary
    del transformation_json["children"][0]["attributes"][0]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_all_information_present_WHEN_attempting_to_create_translation_THEN_create_transform_is_called(
    transformation_reader, transformation_json
):
    transformation_json["children"][0]["config"]["name"] = name = "TranslationName"
    transformation_json["children"][0]["attributes"][1][
        "values"
    ] = transformation_type = "translation"
    transformation_json["children"][0]["config"]["values"] = angle_or_magnitude = 300.0
    transformation_json["children"][0]["attributes"][0]["values"] = units = "mm"
    transformation_json["children"][0]["attributes"][2]["values"] = vector = [
        1.0,
        2.0,
        3.0,
    ]
    transformation_json["children"][0]["attributes"][2]["offset"] = offset_vector = [
        4.0,
        5.0,
        6.0,
    ]
    transformation_json["children"][0]["attributes"][2][
        "offset_units"
    ] = offset_units = "mm"
    depends_on = None

    values = _create_transformation_dataset(angle_or_magnitude, "double", name)

    transformation_reader._create_transformations(transformation_json["children"])
    transformation_reader.parent_component._create_and_add_transform.assert_called_once_with(
        name=name,
        transformation_type=TRANSFORMATION_MAP[transformation_type],
        angle_or_magnitude=angle_or_magnitude,
        units=units,
        vector=QVector3D(*vector),
        depends_on=depends_on,
        values=values,
        offset_vector=QVector3D(*offset_vector),
        offset_units=offset_units,
    )


def test_GIVEN_unrecognised_dtype_WHEN_parsing_dtype_THEN_parse_dtype_returns_empty_string(
    transformation_reader,
):
    n_warnings = len(transformation_reader.warnings)

    assert not transformation_reader._parse_dtype("notvalid", "TransformationName")
    assert len(transformation_reader.warnings) == n_warnings + 1
    assert "dtype" in transformation_reader.warnings[-1].message


@pytest.mark.parametrize("dtype", ["double", "Double", "DOUBLE"])
def test_GIVEN_different_types_of_double_WHEN_parsing_dtype_THEN_parse_dtype_returns_same_value(
    transformation_reader, dtype
):
    assert transformation_reader._parse_dtype(dtype, "TransformationName") == "double"


def test_GIVEN_unrecognised_transformation_type_WHEN_parsing_transformation_type_THEN_parse_transformation_type_returns_empty_string(
    transformation_reader,
):
    n_warnings = len(transformation_reader.warnings)

    assert not transformation_reader._parse_transformation_type(
        "notvalid", "TransformationName"
    )
    assert len(transformation_reader.warnings) == n_warnings + 1
    assert "transformation type" in transformation_reader.warnings[-1].message


def test_GIVEN_invalid_dtype_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    transformation_json["children"][0]["config"]["type"] = "NotAType"
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_invalid_transformation_type_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    transformation_json["children"][0]["attributes"][1]["values"] = "NotAType"
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_transformation_has_depends_on_WHEN_creating_transformations_THEN_details_are_stored_in_dictionary(
    transformation_reader, transformation_json
):
    depends_on_component_name = "test_component"
    depends_on_transform_name = "transformation1"
    depends_on_path = f"entry/instrument/{depends_on_component_name}/transformations/{depends_on_transform_name}"
    transformation_json["children"][0]["config"][
        "name"
    ] = transformation_name = "TransformationName"
    transformation_json["children"][0]["attributes"][3]["values"] = depends_on_path
    transformation_reader._create_transformations(transformation_json["children"])

    transform1 = transformation_reader._transforms_with_dependencies[
        TransformId(PARENT_COMPONENT_NAME, transformation_name)
    ][1]
    transform2 = TransformId(depends_on_component_name, depends_on_transform_name)

    assert (
        transform1 == transform2
    ), "Expected to find details of dependency stored in dictionary"


@pytest.mark.parametrize("depends_on_path", [".", None])
def test_GIVEN_transformation_has_no_depends_on_WHEN_creating_transformations_THEN_details_arent_stored_in_dictionary(
    transformation_reader, transformation_json, depends_on_path
):
    # Having no depends_on string attribute, or it being ".", are both valid and mean it is the
    # last transformation in the depends_on chain
    transformation_json["children"][0]["attributes"][3]["values"] = depends_on_path
    transformation_reader._create_transformations(transformation_json["children"])

    assert (
        transformation_reader._transforms_with_dependencies[
            TransformId(
                PARENT_COMPONENT_NAME,
                transformation_json["children"][0]["config"]["name"],
            )
        ][1]
        is None
    ), (
        "Expected transformation to be added to dictionary but there to be no details"
        "for a transformation dependency"
    )


def test_GIVEN_no_modules_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_with_stream_json
):
    del transformation_with_stream_json["children"][0]["module"]
    transformation_reader._create_transformations(
        transformation_with_stream_json["children"]
    )

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_incorrect_module_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_with_stream_json
):
    transformation_with_stream_json["children"][0][
        "module"
    ] = ":: SOME UNKNOWN MODULE ::"
    transformation_reader._create_transformations(
        transformation_with_stream_json["children"]
    )

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


@pytest.mark.skip(reason="Needs to be fixed after transformation is dealt properly")
def test_GIVEN_all_information_present_in_json_with_stream_WHEN_attempting_to_create_translation_THEN_create_transform_is_called(
    transformation_reader, transformation_with_stream_json
):
    transform_json = transformation_with_stream_json["children"][0]
    transform_json["config"]["name"] = name = "TranslationName"
    transform_json["attributes"][0]["values"] = transformation_type = "translation"
    transform_json["attributes"][1]["values"] = units = "mm"
    transform_json["attributes"][2]["values"] = vector = [
        1.0,
        2.0,
        3.0,
    ]
    depends_on = None
    values = _create_transformation_datastream_group(transform_json, name)
    transformation_reader._create_transformations(
        transformation_with_stream_json["children"]
    )

    transformation_reader.parent_component._create_and_add_transform.assert_called_once_with(
        name=name,
        transformation_type=TRANSFORMATION_MAP[transformation_type],
        angle_or_magnitude=0.0,
        units=units,
        vector=QVector3D(*vector),
        depends_on=depends_on,
        values=values,
    )
