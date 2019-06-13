import pytest

from nexus_constructor.component_type import __list_base_class_files


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

