import h5py
from mock import Mock
from nexus_constructor.nexus.nexus_wrapper import (
    NexusWrapper,
    append_nxs_extension,
    get_nx_class,
)
import pytest

pytest.skip("Disabled whilst working on model change", allow_module_level=True)


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


def test_GIVEN_entry_group_with_one_instrument_group_WHEN_getting_instrument_group_from_entry_THEN_group_is_returned(
    file,
):
    entry = file.create_group("entry")
    entry.attrs["NX_class"] = "NXentry"

    inst_group = entry.create_group("instrument")
    inst_group.attrs["NX_class"] = "NXinstrument"

    wrapper = NexusWrapper(filename="test_nw")
    wrapper.load_file(entry, file)

    assert wrapper.instrument == inst_group
    assert wrapper.entry == entry
    assert wrapper.nexus_file == file


def test_GIVEN_multiple_entry_groups_WHEN_getting_instrument_group_from_entry_THEN_first_group_is_returned_and_others_are_ignored(
    file,
):
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


def test_GIVEN_single_entry_group_with_instrument_group_WHEN_finding_entry_THEN_file_is_loaded_correctly(
    file,
):
    entry = file.create_group("entry")
    entry.attrs["NX_class"] = "NXentry"

    inst_group = entry.create_group("instrument")
    inst_group.attrs["NX_class"] = "NXinstrument"

    wrapper = NexusWrapper(filename="test_nw5")

    wrapper.find_entries_in_file(file)

    assert wrapper.nexus_file == file
    assert wrapper.entry == entry
    assert wrapper.instrument == inst_group


def test_GIVEN_no_entry_or_instrument_in_file_WHEN_finding_entry_THEN_default_entry_and_instrument_are_created(
    file,
):
    wrapper = NexusWrapper(filename="test_nw5")
    wrapper.find_entries_in_file(file)

    assert isinstance(wrapper.entry, h5py.Group)
    assert isinstance(wrapper.instrument, h5py.Group)


def test_GIVEN_multiple_entry_groups_in_file_WHEN_finding_entry_THEN_signal_is_emitted_with_entry_options(
    file,
):

    entry = file.create_group("entry")
    # Test with byte string as well as python string.
    entry.attrs["NX_class"] = b"NXentry"

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


def test_GIVEN_group_without_nx_class_WHEN_getting_nx_class_THEN_returns_none(file):
    entry = file.create_group("entry")
    assert get_nx_class(entry) is None


def test_GIVEN_group_with_nx_class_as_str_WHEN_getting_nx_class_THEN_returns_nx_class_as_str(
    file,
):

    entry = file.create_group("entry")
    nx_class = "NXentry"
    entry.attrs["NX_class"] = nx_class
    assert get_nx_class(entry) == nx_class


def test_GIVEN_group_with_nx_class_as_bytes_WHEN_getting_nx_class_THEN_returns_nx_class_as_str(
    file,
):

    entry = file.create_group("entry")
    nx_class = b"NXentry"
    entry.attrs["NX_class"] = nx_class
    assert get_nx_class(entry) == str(nx_class, encoding="utf-8")


def test_GIVEN_group_with_bytes_attribute_WHEN_getting_attribute_value_THEN_returns_value_as_str(
    nexus_wrapper,
):

    test_group = nexus_wrapper.nexus_file.create_group("test_group")
    attr_value = b"test_attr_value"
    attr_name = "test_attr"
    test_group.attrs[attr_name] = attr_value

    attr_value_as_str = attr_value.decode("utf-8")

    assert nexus_wrapper.get_attribute_value(test_group, attr_name) == attr_value_as_str


def test_GIVEN_variable_length_string_type_dataset_WHEN_getting_value_THEN_returned_as_str(
    nexus_wrapper,
):
    dataset_name = "vlen_str_dataset"
    string_data = b"This is a string"
    nexus_wrapper.nexus_file.create_dataset(
        dataset_name, dtype=h5py.special_dtype(vlen=str), data=string_data
    )

    assert nexus_wrapper.get_field_value(
        nexus_wrapper.nexus_file, dataset_name
    ) == string_data.decode("utf8")
    assert isinstance(
        nexus_wrapper.get_field_value(nexus_wrapper.nexus_file, dataset_name), str
    )
