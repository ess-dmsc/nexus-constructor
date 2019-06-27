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
    instrument.add_component(name, component_type, description)

    check_if_component_is_in_component_list(
        component_type, description, instrument, name, expect_component_present=True
    )


def test_GIVEN_instrument_with_component_WHEN_component_is_removed_THEN_components_list_does_not_contain_component():
    wrapper = NexusWrapper("test_components_list")
    instrument = Instrument(wrapper)

    component_type = "NXcrystal"
    name = "test_crystal"
    description = "shiny"
    test_component = instrument.add_component(name, component_type, description)

    # Test component should be in list
    check_if_component_is_in_component_list(
        component_type, description, instrument, name, expect_component_present=True
    )

    instrument.remove_component(test_component)

    # Test component should no longer be in list
    check_if_component_is_in_component_list(
        component_type, description, instrument, name, expect_component_present=False
    )
