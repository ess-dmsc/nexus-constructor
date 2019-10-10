import pytest
import h5py
import numpy as np
from nexus_constructor.json.filewriter_json_reader import json_to_nexus


def is_nexus_class(group: h5py.Group, class_name: str):
    if "NX_class" in group.attrs.keys():
        return group.attrs["NX_class"] == class_name
    return False


def test_GIVEN_empty_json_string_WHEN_json_to_nexus_called_THEN_error_is_raised():
    with pytest.raises(ValueError):
        json_to_nexus("")


def test_GIVEN_invalid_json_string_WHEN_json_to_nexus_called_THEN_error_is_raised():
    with pytest.raises(ValueError):
        json_to_nexus("{")


def test_GIVEN_json_containing_group_WHEN_json_to_nexus_called_THEN_group_created_in_NeXus():
    group_name = "test_group"
    test_json = f"""
    {{
      "nexus_structure": {{
        "children": [
          {{
            "type": "group",
            "name": "{group_name}",
            "children": []
          }}
        ]
      }}
    }}
    """
    nexus_file = json_to_nexus(test_json)
    assert group_name in nexus_file
    assert isinstance(nexus_file[group_name], h5py.Group)


def test_GIVEN_json_containing_entry_group_WHEN_json_to_nexus_called_THEN_entry_created_in_NeXus():
    test_json = """
    {
      "nexus_structure": {
        "children": [
          {
            "type": "group",
            "name": "test_entry",
            "children": [],
            "attributes": [
              {
                "name": "NX_class",
                "values": "NXentry"
              }
            ]
          }
        ]
      }
    }
    """
    nexus_file = json_to_nexus(test_json)
    assert "test_entry" in nexus_file
    assert is_nexus_class(nexus_file["test_entry"], "NXentry")


def test_GIVEN_json_containing_dataset_WHEN_json_to_nexus_called_THEN_dataset_created_in_NeXus():
    dataset_name = "test_dataset"
    dataset_value = 1817.0
    attribute_name = "test_attribute"
    attribute_value = 42
    test_json = f"""
    {{
      "nexus_structure": {{
        "children": [
          {{
            "type": "dataset",
            "name": "{dataset_name}",
            "attributes": [
              {{
                "name": "{attribute_name}",
                "values": {attribute_value}
              }}
            ],
            "dataset": {{
              "type": "float",
              "size": [1]
            }},
            "values": [{dataset_value}]
          }}
        ]
      }}
    }}
    """
    nexus_file = json_to_nexus(test_json)

    assert dataset_name in nexus_file
    assert np.isclose(nexus_file[dataset_name][...], dataset_value)
    assert attribute_name in nexus_file[dataset_name].attrs.keys()
    assert nexus_file[dataset_name].attrs[attribute_name] == attribute_value
