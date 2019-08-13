import numpy as np
import pytest
from mock import Mock

from nexus_constructor.nexus.nexus_wrapper import (
    NexusWrapper,
    append_nxs_extension,
    get_nx_class,
)
from nexus_constructor.pixel_data import PixelMapping, PixelGrid, CountDirection, Corner
from nexus_constructor.pixel_data_to_nexus_utils import (
    pixel_grid_x_offsets,
    pixel_grid_y_offsets,
    pixel_grid_z_offsets,
    pixel_grid_detector_ids,
)
from tests.test_nexus_to_json import create_in_memory_file

global file_count
file_count = 0


@pytest.fixture(scope="function")
def nexus_file():
    global file_count
    file_count += 1
    return create_in_memory_file("test_nw" + str(file_count - 1))


@pytest.fixture(scope="function")
def entry(nexus_file):
    return nexus_file.create_group("entry")


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


def test_GIVEN_multiple_entry_groups_in_file_WHEN_finding_entry_THEN_signal_is_emitted_with_entry_options():
    file = create_in_memory_file("test_nw6")

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


def test_GIVEN_group_without_nx_class_WHEN_getting_nx_class_THEN_returns_none():
    file = create_in_memory_file("test_nw7")
    entry = file.create_group("entry")
    assert get_nx_class(entry) is None


def test_GIVEN_group_with_nx_class_as_str_WHEN_getting_nx_class_THEN_returns_nx_class_as_str():
    file = create_in_memory_file("test_nw8")
    entry = file.create_group("entry")
    nx_class = "NXentry"
    entry.attrs["NX_class"] = nx_class
    assert get_nx_class(entry) == nx_class


def test_GIVEN_group_with_nx_class_as_bytes_WHEN_getting_nx_class_THEN_returns_nx_class_as_str():
    file = create_in_memory_file("test_nw9")
    entry = file.create_group("entry")
    nx_class = b"NXentry"
    entry.attrs["NX_class"] = nx_class
    assert get_nx_class(entry) == str(nx_class, encoding="utf-8")


def test_GIVEN_pixel_mapping_WHEN_recording_pixel_data_to_nxdetector_THEN_pixel_ids_in_nexus_file_match_pixel_ids_in_mapping_object(
    nexus_file, entry
):

    nx_class = "NXdetector"
    entry.attrs["NX_class"] = nx_class

    pixel_id_list = [i for i in range(5)]
    pixel_data = PixelMapping(pixel_id_list)

    nexus_wrapper = NexusWrapper("text_nw11")
    nexus_wrapper.record_pixel_data(entry, nx_class, pixel_data)

    pixel_ids = entry.get("detector_number")
    pixel_id_array = np.array(pixel_ids)

    assert np.array_equal(pixel_id_array, np.array(pixel_id_list))


def test_GIVEN_pixel_grid_WHEN_recording_pixel_data_to_nxdetector_THEN_pixel_data_in_nexus_file_matches_pixel_data_in_pixel_grid_object(
    nexus_file, entry
):

    nx_class = "NXdetector"
    entry.attrs["NX_class"] = nx_class

    pixel_grid = PixelGrid(
        rows=5,
        columns=6,
        row_height=0.7,
        col_width=0.5,
        first_id=0,
        count_direction=CountDirection.COLUMN,
        initial_count_corner=Corner.BOTTOM_RIGHT,
    )

    nexus_wrapper = NexusWrapper("pixel_grid_test")
    nexus_wrapper.record_pixel_data(entry, nx_class, pixel_grid)

    assert np.array_equal(entry.get("x_pixel_offset"), pixel_grid_x_offsets(pixel_grid))
    assert np.array_equal(entry.get("y_pixel_offset"), pixel_grid_y_offsets(pixel_grid))
    assert np.array_equal(entry.get("z_pixel_offset"), pixel_grid_z_offsets(pixel_grid))
    assert np.array_equal(
        entry.get("detector_number"), pixel_grid_detector_ids(pixel_grid)
    )
