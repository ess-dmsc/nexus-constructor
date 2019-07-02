from nexus_constructor.nexus.nexus_wrapper import NexusWrapper, append_nxs_extension
from tests.test_nexus_to_json import create_in_memory_file


def test_GIVEN_nothing_WHEN_creating_nexus_wrapper_THEN_file_contains_entry_group_with_correct_nx_class():
    wrapper = NexusWrapper("contains_entry")
    assert wrapper.nexus_file["entry"].attrs["NX_class"] == "NXentry"


def test_GIVEN_nothing_WHEN_creating_nexus_wrapper_THEN_file_contains_instrument_group_with_correct_nx_class():
    wrapper = NexusWrapper("contains_instrument")
    assert wrapper.nexus_file["entry/instrument"].attrs["NX_class"] == "NXinstrument"


def test_GIVEN_nothing_WHEN_creating_nexus_wrapper_THEN_entry_group_contains_sample():
    wrapper = NexusWrapper("entry_sample")
    assert wrapper.nexus_file["entry/sample"].attrs["NX_class"] == "NXsample"


def test_nxs_is_appended_to_filename():
    test_filename = "banana"
    assert append_nxs_extension(test_filename) == f"{test_filename}.nxs"


def test_nxs_not_appended_to_filename_if_already_present():
    test_filename = "banana.nxs"
    assert append_nxs_extension(test_filename) == f"{test_filename}"


def test_GIVEN_entry_group_with_one_instrument_group_WHEN_getting_instrument_group_from_entry_THEN_group_is_returned():
    file = create_in_memory_file("test_nw1")

    entry = file.create_group("entry")
    entry.attrs["NX_class"] = "NXentry"

    inst_group = entry.create_group("instrument")
    inst_group.attrs["NX_class"] = "NXinstrument"

    wrapper = NexusWrapper(filename="test_nw")
    wrapper.load_file(entry, file)

    assert wrapper.instrument == inst_group
    assert wrapper.entry == entry
    assert wrapper.nexus_file == file


def test_GIVEN_multiple_entry_groups_WHEN_getting_instrument_group_from_entry_THEN_first_group_is_returned_and_others_are_ignored():
    file = create_in_memory_file("test_nw3")

    entry = file.create_group("entry")
    entry.attrs["NX_class"] = "NXentry"

    inst_group = entry.create_group("instrument")
    inst_group.attrs["NX_class"] = "NXinstrument"

    inst_group2 = entry.create_group("instrument2")
    inst_group2.attrs["NX_class"] = "NXinstrument"

    wrapper = NexusWrapper(filename="test_nw2")
    wrapper.load_file(entry, file)

    assert wrapper.nexus_file == file
    assert wrapper.entry == entry
    assert wrapper.instrument == inst_group
