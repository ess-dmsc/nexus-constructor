import h5py
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper, append_nxs_extension
from nexus_constructor.transformations import TransformationModel


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


class NexusWrapperNoInit(NexusWrapper):
    def __init__(self):
        pass


def test_dependents_list_is_created_on_file_load():
    """
    The dependents list for transforms is stored in the "dependent_of" attribute,
    which is not part of the NeXus standard,
    we therefore cannot rely on it being present and correct in a file we load.
    This test makes sure that we generate this information on file load.
    """

    # Create minimal test file with some transformations but no "dependent_of" attributes
    in_memory_test_file = h5py.File(
        "test_file", mode="x", driver="core", backing_store=False
    )
    entry_group = in_memory_test_file.create_group("entry")
    entry_group.attrs["NX_class"] = "NXentry"
    instrument_group = entry_group.create_group("instrument")
    instrument_group.attrs["NX_class"] = "NXinstrument"
    transforms_group = instrument_group.create_group("transformations")
    transforms_group.attrs["NX_class"] = "NXtransformations"
    transform_1 = transforms_group.create_dataset("transform_1", data=42)
    transform_2 = transforms_group.create_dataset("transform_2", data=42)
    transform_3 = transforms_group.create_dataset("transform_3", data=42)
    transform_4 = transforms_group.create_dataset("transform_4", data=42)
    transform_2.attrs["depends_on"] = transform_1.name
    transform_3.attrs["depends_on"] = transform_2.name
    transform_4.attrs["depends_on"] = transform_2.name

    nexus_wrapper = NexusWrapperNoInit()
    nexus_wrapper._load_file(in_memory_test_file)

    transform_1_loaded = TransformationModel(nexus_wrapper, transform_1)
    assert (
        len(transform_1_loaded.get_dependents()) == 1
    ), "Expected transform 1 to have a registered dependent (transform 2)"

    transform_2_loaded = TransformationModel(nexus_wrapper, transform_2)
    assert (
        len(transform_2_loaded.get_dependents()) == 2
    ), "Expected transform 2 to have 2 registered dependents (transforms 3 and 4)"
