import pytest

from nexus_constructor.model.component import Component
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


def test_group_depth_returns_expected_tree_depth():
    entry = Group("entry")
    sample = Component("sample", parent_node=entry)
    instrument = Group("instrument", parent_node=entry)
    g1 = Group("g1", parent_node=instrument)
    g2 = Group("g2", parent_node=instrument)
    g21 = Group("g21", parent_node=g2)

    c1 = Component("c1", parent_node=instrument)
    c2 = Group("c2", parent_node=instrument)

    dataset = Dataset(name="dataset", values=0, parent_node=sample)
    entry.children = [sample, instrument]
    sample.children = [g1, g2, dataset]
    g2.children = [g21]
    instrument.children = [c1, c2]

    assert entry.tree_depth() == 4
    assert sample.tree_depth() == 3
    assert instrument.tree_depth() == 2
