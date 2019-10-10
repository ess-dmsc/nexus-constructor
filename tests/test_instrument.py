import h5py
from nexus_constructor.transformations import Transformation
from nexus_constructor.instrument import _convert_name_with_spaces, Instrument
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper


def test_GIVEN_name_with_spaces_WHEN_converting_name_with_spaces_THEN_converts_spaces_in_name_to_underscores():
    name = "test name"
    assert _convert_name_with_spaces(name) == name.replace(" ", "_")


def test_GIVEN_name_without_spaces_WHEN_converting_name_with_spaces_THEN_name_does_not_change():
    name = "test_name"
    assert _convert_name_with_spaces(name) == name


def test_GIVEN_nothing_WHEN_getting_components_list_THEN_list_contains_sample_and_no_components():
    wrapper = NexusWrapper("component_list_with_sample")
    instrument = Instrument(wrapper)
    assert len(instrument.get_component_list()) == 1


def check_if_component_is_in_component_list(
    component_type, description, instrument, name, expect_component_present
):
    component_list = instrument.get_component_list()
    found_component = False
    for component in component_list:
        if component.name == name:
            found_component = True
            assert component.description == description
            assert component.nx_class == component_type
    assert found_component == expect_component_present


def test_GIVEN_component_WHEN_adding_component_THEN_components_list_contains_added_component():
    wrapper = NexusWrapper("test_components_list")
    instrument = Instrument(wrapper)

    component_type = "NXcrystal"
    name = "test_crystal"
    description = "shiny"
    instrument.create_component(name, component_type, description)

    check_if_component_is_in_component_list(
        component_type, description, instrument, name, expect_component_present=True
    )


def test_GIVEN_instrument_with_component_WHEN_component_is_removed_THEN_components_list_does_not_contain_component():
    wrapper = NexusWrapper("test_components_list")
    instrument = Instrument(wrapper)

    component_type = "NXcrystal"
    name = "test_crystal"
    description = "shiny"
    test_component = instrument.create_component(name, component_type, description)

    # Test component should be in list
    check_if_component_is_in_component_list(
        component_type, description, instrument, name, expect_component_present=True
    )

    instrument.remove_component(test_component)

    # Test component should no longer be in list
    check_if_component_is_in_component_list(
        component_type, description, instrument, name, expect_component_present=False
    )


def test_GIVEN_instrument_with_one_stream_WHEN_finding_streams_THEN_streams_dictionary_is_populated():
    wrapper = NexusWrapper("test_streams")
    instrument = Instrument(wrapper)

    component_type = "NCstream"
    name = "test_crystal"
    description = "shiny"
    test_component = instrument.create_component(name, component_type, description)

    topic_field_name = "topic"
    topic_name = "something"

    test_component.group.create_dataset(name=topic_field_name, data=topic_name)
    streams_dict = instrument.get_streams()

    assert streams_dict[test_component.absolute_path][topic_field_name] == topic_name


def test_GIVEN_instrument_with_stream_with_incorrect_nx_class_for_stream_WHEN_finding_streams_THEN_streams_dictionary_is_empty():
    wrapper = NexusWrapper("test_streams_none")
    instrument = Instrument(wrapper)

    component_type = "NXcrystal"
    name = "test_crystal"
    description = "shiny"
    test_component = instrument.create_component(name, component_type, description)

    topic_field_name = "topic"
    topic_name = "something"

    test_component.group.create_dataset(name=topic_field_name, data=topic_name)
    streams_dict = instrument.get_streams()
    assert not streams_dict


def test_dependents_list_is_created_by_instrument():
    """
    The dependents list for transforms is stored in the "dependent_of" attribute,
    which is not part of the NeXus standard,
    we therefore cannot rely on it being present and correct in a file we load.
    This test makes sure that instrument generates this information in the wrapped NeXus file it is given.
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

    nexus_wrapper = NexusWrapper("test_file_with_transforms")
    nexus_wrapper.load_file(entry_group, in_memory_test_file)
    Instrument(nexus_wrapper)

    transform_1_loaded = Transformation(nexus_wrapper, transform_1)
    assert (
        len(transform_1_loaded.get_dependents()) == 1
    ), "Expected transform 1 to have a registered dependent (transform 2)"

    transform_2_loaded = Transformation(nexus_wrapper, transform_2)
    assert (
        len(transform_2_loaded.get_dependents()) == 2
    ), "Expected transform 2 to have 2 registered dependents (transforms 3 and 4)"


def test_GIVEN_dot_separated_field_name_WHEN_getting_streams_THEN_dict_is_returned_with_correct_structure():
    wrapper = NexusWrapper("test_streams_dict")
    inst = Instrument(wrapper)

    streams_group = wrapper.entry.create_group("streams")
    streams_group.attrs["NX_class"] = "NCstream"

    name = "nexus.indices.index_every_mb"
    val = 1000

    streams_group.create_dataset(name=name, dtype=int, data=val)

    streams = inst.get_streams()

    assert "nexus" in streams["/entry/streams"]
    assert "indices" in streams["/entry/streams"]["nexus"]
    assert streams["/entry/streams"]["nexus"]["indices"]["index_every_mb"] == val


def test_GIVEN_several_dot_separated_field_names_with_similar_prefixes_WHEN_getting_streams_THEN_dict_is_returned_with_correct_structure():
    wrapper = NexusWrapper("test_streams_dict_multiple")
    inst = Instrument(wrapper)

    streams_group = wrapper.entry.create_group("streams")
    streams_group.attrs["NX_class"] = "NCstream"

    name = "nexus.indices.index_every_mb"
    val = 1000

    streams_group.create_dataset(name=name, dtype=int, data=val)

    name2 = "nexus.indices.index_every_kb"
    val2 = 2000

    streams_group.create_dataset(name=name2, dtype=int, data=val2)

    streams = inst.get_streams()

    assert "nexus" in streams["/entry/streams"]
    assert "indices" in streams["/entry/streams"]["nexus"]
    assert streams["/entry/streams"]["nexus"]["indices"]["index_every_mb"] == val
    assert streams["/entry/streams"]["nexus"]["indices"]["index_every_kb"] == val2
