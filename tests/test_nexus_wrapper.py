from nexus_constructor.nexus.nexus_wrapper import NexusWrapper, append_nxs_extension


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
