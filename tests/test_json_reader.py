import pytest
import h5py
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
