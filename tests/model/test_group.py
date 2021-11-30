import pytest

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.group import Group
from nexus_constructor.model.module import Dataset


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


def test_group_is_component_WHEN_depends_on_exists():
    test_group = Group("test_group")
    test_group.children.append(
        Dataset(parent_node=test_group, name=CommonAttrs.DEPENDS_ON, values="some_path")
    )
    assert test_group.is_component()


def test_group_is_not_component_WHEN_depends_on_is_missing():
    test_group = Group("test_group")
    test_group.children.append(Dataset(parent_node=test_group, name="data", values=1))
    assert not test_group.is_component()
