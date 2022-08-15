import pytest

from nexus_constructor.component_type import (
    __list_base_class_files,
    _create_base_class_dict,
)


def test_GIVEN_list_of_files_all_ending_with_nxdl_WHEN_list_base_class_files_THEN_yields_correct_files():
    list_of_files = ["something.nxdl.xml", "somethingelse.nxdl.xml", "test.nxdl.xml"]

    gen = __list_base_class_files(list_of_files)

    for i in range(len(list_of_files)):
        assert next(gen) == list_of_files[i]


def test_GIVEN_list_of_files_not_ending_in_nxdl_WHEN_listing_base_class_files_THEN_does_not_yield():
    list_of_files = ["README.md", "test.nxs", "sample.json"]

    gen = __list_base_class_files(list_of_files)

    with pytest.raises(StopIteration):
        next(gen)


def test_GIVEN_list_of_files_some_ending_with_nxdl_WHEN_listing_base_class_files_THEN_yields_correct_items():
    list_of_files = ["something.nxdl.xml", "README.md", "test.nxdl.xml"]

    gen = __list_base_class_files(list_of_files)

    assert next(gen) == list_of_files[0]
    assert next(gen) == list_of_files[2]

    with pytest.raises(StopIteration):
        next(gen)


def test_GIVEN_valid_base_class_containing_name_WHEN_creating_base_class_dict_THEN_dict_contains_base_class_with_name():
    class_name = "NXtest"
    xml = f"""
    <definition
    name="{class_name}"
    type="group" extends="NXobject">
    </definition>
    """

    base_classes = dict()
    component_base_classes = dict()
    _create_base_class_dict(xml, None, base_classes, component_base_classes)

    assert class_name in base_classes.keys()


def test_GIVEN_a_valid_base_class_containing_name_key_and_name_field_WHEN_creating_base_class_dict_THEN_dict_contains_base_class_with_name_as_key_and_name_field():
    class_name = "NXtest"

    xml = f"""<definition
    name="{class_name}"
    type="group" extends="NXobject">
        <field name="name">
            <doc>Name of user responsible for this entry</doc>
        </field>
    </definition>
    """

    base_classes = dict()
    component_base_classes = dict()
    _create_base_class_dict(xml, None, base_classes, component_base_classes)
    assert class_name in base_classes.keys()
    assert ("name", "string", "") in base_classes[class_name]


def test_GIVEN_a_valid_base_class_with_no_fields_WHEN_creating_base_class_dict_THEN_dict_contains_empty_list_for_value():
    class_name = "NXtest"
    xml = f"""
        <definition
        name="{class_name}"
        type="group" extends="NXobject">
        </definition>
        """

    base_classes = dict()
    component_base_classes = dict()
    _create_base_class_dict(xml, None, base_classes, component_base_classes)

    assert not base_classes[class_name]


def test_GIVEN_a_valid_base_class_that_is_in_excludelist_WHEN_creating_base_class_dict_THEN_dict_stays_empty():
    class_name = "NXtest"
    xml = f"""
            <definition
            name="{class_name}"
            type="group" extends="NXobject">
            </definition>
            """
    base_classes = dict()
    component_base_classes = dict()
    _create_base_class_dict(xml, [class_name], base_classes, component_base_classes)

    assert not base_classes
