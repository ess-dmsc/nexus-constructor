from nexus_constructor.transformations import Transformation
from nexus_constructor.model.entry import Instrument, _convert_name_with_spaces
from tests.test_utils import NX_CLASS_DEFINITIONS
import pytest


def test_GIVEN_name_with_spaces_WHEN_converting_name_with_spaces_THEN_converts_spaces_in_name_to_underscores():
    name = "test name"
    assert _convert_name_with_spaces(name) == name.replace(" ", "_")


def test_GIVEN_name_without_spaces_WHEN_converting_name_with_spaces_THEN_name_does_not_change():
    name = "test_name"
    assert _convert_name_with_spaces(name) == name


pytest.skip("Disabled whilst working on model change", allow_module_level=True)


def test_GIVEN_nothing_WHEN_getting_components_list_THEN_list_contains_sample_and_no_components(
    nexus_wrapper,
):
    instrument = Instrument(nexus_wrapper, NX_CLASS_DEFINITIONS)
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


def test_GIVEN_component_WHEN_adding_component_THEN_components_list_contains_added_component(
    nexus_wrapper,
):
    instrument = Instrument(nexus_wrapper, NX_CLASS_DEFINITIONS)

    component_type = "NXcrystal"
    name = "test_crystal"
    description = "shiny"
    instrument.create_component(name, component_type, description)

    check_if_component_is_in_component_list(
        component_type, description, instrument, name, expect_component_present=True
    )


def test_GIVEN_instrument_with_component_WHEN_component_is_removed_THEN_components_list_does_not_contain_component(
    nexus_wrapper,
):
    instrument = Instrument(nexus_wrapper, NX_CLASS_DEFINITIONS)

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


def test_dependents_list_is_created_by_instrument(file, nexus_wrapper):
    """
    The dependents list for transforms is stored in the "dependent_of" attribute,
    which is not part of the NeXus standard,
    we therefore cannot rely on it being present and correct in a file we load.
    This test makes sure that instrument generates this information in the wrapped NeXus file it is given.
    """

    # Create minimal test file with some transformations but no "dependent_of" attributes
    entry_group = file.create_group("entry")
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

    nexus_wrapper.load_file(entry_group, file)
    Instrument(nexus_wrapper, NX_CLASS_DEFINITIONS)

    transform_1_loaded = Transformation(nexus_wrapper, transform_1)
    assert (
        len(transform_1_loaded.dependents) == 1
    ), "Expected transform 1 to have a registered dependent (transform 2)"

    transform_2_loaded = Transformation(nexus_wrapper, transform_2)
    assert (
        len(transform_2_loaded.dependents) == 2
    ), "Expected transform 2 to have 2 registered dependents (transforms 3 and 4)"


def test_dependent_is_created_by_instrument_if_depends_on_is_relative(
    file, nexus_wrapper
):
    entry_group = file.create_group("entry")
    entry_group.attrs["NX_class"] = "NXentry"
    monitor_group = entry_group.create_group("monitor1")
    monitor_group.attrs["NX_class"] = "NXmonitor"

    monitor_group.create_dataset("depends_on", data=b"transformations/translation1")

    transformations_group = monitor_group.create_group("transformations")
    transformations_group.attrs["NX_class"] = "NXtransformations"
    transform_1 = transformations_group.create_dataset("translation1", data=1)

    nexus_wrapper.load_file(entry_group, file)
    Instrument(nexus_wrapper, NX_CLASS_DEFINITIONS)

    transform_1_loaded = Transformation(nexus_wrapper, transform_1)
    assert transform_1_loaded.dataset.attrs["NCdependee_of"][0] == "/entry/monitor1"


def test_dependee_of_contains_both_components_when_generating_dependee_of_chain_with_mixture_of_absolute_and_relative_paths(
    file, nexus_wrapper
):
    entry_group = file.create_group("entry")
    entry_group.attrs["NX_class"] = "NXentry"
    instrument_group = entry_group.create_group("instrument")
    instrument_group.attrs["NX_class"] = "NXinstrument"

    component_a = instrument_group.create_group("a")
    component_a.attrs["NX_class"] = "NXaperture"
    transforms_group = component_a.create_group("Transforms1")
    transform_1 = transforms_group.create_dataset("transform1", data=1.0)
    # Relative path to transform
    component_a.create_dataset("depends_on", data="Transforms1/transform1")

    component_b = instrument_group.create_group("b")
    component_b.attrs["NX_class"] = "NXaperture"
    # Absolute path to transform
    component_b.create_dataset(
        "depends_on", data="/entry/instrument/a/Transforms1/transform1"
    )

    nexus_wrapper.load_file(entry_group, file)
    Instrument(nexus_wrapper, NX_CLASS_DEFINITIONS)
    transform_1_loaded = Transformation(nexus_wrapper, transform_1)

    # Check both relative and absolute are in dependee_of list
    assert component_a.name in transform_1_loaded.dataset.attrs["NCdependee_of"]
    assert component_b.name in transform_1_loaded.dataset.attrs["NCdependee_of"]
