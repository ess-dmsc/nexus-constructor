import pytest

from nexus_constructor.model.group import Group


def test_get_field_value_throws_if_field_does_not_exist():
    group = Group("test_group")

    with pytest.raises(AttributeError):
        group.get_field_value("nonexistentfield")


def test_group_as_dict_contains_expected_keys():
    input_name = "test_group"
    test_group = Group("test_group")
    dictionary_output = test_group.as_dict([])
    for expected_key in (
        "name",
        "type",
        "children",
    ):  # Attributes should not be included by default if there are none, unlike children
        assert expected_key in dictionary_output.keys()

    assert dictionary_output["name"] == input_name
