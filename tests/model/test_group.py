import pytest

from nexus_constructor.model.group import Group


def test_get_field_value_throws_if_field_does_not_exist():

    group = Group("test_group")

    with pytest.raises(AttributeError):
        group.get_field_value("nonexistentfield")
