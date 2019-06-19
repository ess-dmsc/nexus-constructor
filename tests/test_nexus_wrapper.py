from nexus_constructor.nexus_wrapper import NexusWrapper, convert_name_with_spaces
from nexus_constructor.qml_models.geometry_models import NoShapeModel


def test_GIVEN_nothing_WHEN_creating_nexus_wrapper_THEN_file_contains_entry_group_with_correct_nx_class():
    wrapper = NexusWrapper("contains_entry")
    assert wrapper.entry_group.attrs["NX_class"] == "NXentry"


def test_GIVEN_nothing_WHEN_creating_nexus_wrapper_THEN_file_contains_instrument_group_with_correct_nx_class():
    wrapper = NexusWrapper("contains_instrument")
    assert wrapper.instrument_group.attrs["NX_class"] == "NXinstrument"


def test_GIVEN_nothing_WHEN_getting_components_list_THEN_list_contains_sample_and_no_components():
    wrapper = NexusWrapper("component_list_with_sample")
    assert len(wrapper.get_component_list().components) == 1


def test_GIVEN_nothing_WHEN_creating_nexus_wrapper_THEN_entry_group_contains_sample():
    wrapper = NexusWrapper("entry_sample")
    assert wrapper.entry_group["sample"].attrs["NX_class"] == "NXsample"


def test_GIVEN_component_WHEN_adding_component_THEN_components_list_contains_added_component():
    wrapper = NexusWrapper("test_components_list")

    component_type = "NXcrystal"
    name = "test_crystal"
    description = "shiny"
    wrapper.add_component(component_type, name, description, NoShapeModel())

    component_list = wrapper.get_component_list().components
    assert len(component_list) == 2
    component_in_list = component_list[1]
    assert component_in_list.name == name
    assert component_in_list.description == description
    assert component_in_list.nx_class == component_type


def test_GIVEN_component_WHEN_adding_component_THEN_nexus_file_contains_added_component():
    wrapper = NexusWrapper("test_component")

    component_type = "NXcrystal"
    name = "test_crystal"
    description = "shiny"
    wrapper.add_component(component_type, name, description, NoShapeModel())

    assert name in wrapper.instrument_group
    component_in_nexus_file = wrapper.instrument_group[name]
    assert component_in_nexus_file.attrs["NX_class"] == component_type


def test_GIVEN_name_with_spaces_WHEN_converting_name_with_spaces_THEN_converts_spaces_in_name_to_underscores():
    name = "test name"
    assert convert_name_with_spaces(name) == name.replace(" ", "_")


def test_GIVEN_name_without_spaces_WHEN_converting_name_with_spaces_THEN_name_does_not_change():
    name = "test_name"
    assert convert_name_with_spaces(name) == name
