from nexus_constructor.instrument import convert_name_with_spaces, Instrument
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper


def test_GIVEN_name_with_spaces_WHEN_converting_name_with_spaces_THEN_converts_spaces_in_name_to_underscores():
    name = "test name"
    assert convert_name_with_spaces(name) == name.replace(" ", "_")


def test_GIVEN_name_without_spaces_WHEN_converting_name_with_spaces_THEN_name_does_not_change():
    name = "test_name"
    assert convert_name_with_spaces(name) == name


def test_GIVEN_nothing_WHEN_getting_components_list_THEN_list_contains_sample_and_no_components():
    wrapper = NexusWrapper("component_list_with_sample")
    instrument = Instrument(wrapper)
    assert len(instrument.get_component_list()) == 1


def test_GIVEN_component_WHEN_adding_component_THEN_components_list_contains_added_component():
    wrapper = NexusWrapper("test_components_list")
    instrument = Instrument(wrapper)

    component_type = "NXcrystal"
    name = "test_crystal"
    description = "shiny"
    instrument.add_component(name, component_type, description)

    component_list = instrument.get_component_list()
    assert len(component_list) == 2
    found_component = False
    for component in component_list:
        if component.name == name:
            found_component = True
            assert component.description == description
            assert component.nx_class == component_type
    assert found_component
