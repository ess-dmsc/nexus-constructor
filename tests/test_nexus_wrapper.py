from mock import Mock

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


def test_GIVEN_single_entry_group_with_instrument_group_WHEN_finding_entry_THEN_file_is_loaded_correctly():
    file = create_in_memory_file("test_nw4")

    entry = file.create_group("entry")
    entry.attrs["NX_class"] = "NXentry"

    inst_group = entry.create_group("instrument")
    inst_group.attrs["NX_class"] = "NXinstrument"

    wrapper = NexusWrapper(filename="test_nw5")

    wrapper.find_entries_in_file(file)

    assert wrapper.nexus_file == file
    assert wrapper.entry == entry
    assert wrapper.instrument == inst_group


def test_GIVEN_multiple_entry_groups_in_file_WHEN_finding_entry_THEN_signal_is_emitted_with_correct_arguments():
    file = create_in_memory_file("test_nw6")

    entry = file.create_group("entry")
    entry.attrs["NX_class"] = "NXentry"

    inst_group = entry.create_group("instrument")
    inst_group.attrs["NX_class"] = "NXinstrument"

    entry2 = file.create_group("entry2")
    entry2.attrs["NX_class"] = "NXentry"

    inst_group2 = entry2.create_group("instrument2")
    inst_group2.attrs["NX_class"] = "NXinstrument"

    wrapper = NexusWrapper(filename="test_nw7")
    wrapper.show_entries_dialog = Mock()
    wrapper.show_entries_dialog.emit = Mock()

    wrapper.find_entries_in_file(file)

    expected_entry_dict = {entry.name: entry, entry2.name: entry2}

    assert wrapper.show_entries_dialog.emit.called_once_with(expected_entry_dict, file)
