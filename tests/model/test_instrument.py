from nexus_constructor.model.instrument import Instrument, SAMPLE_NAME
from nexus_constructor.model.component import Component


def test_instrument_as_dict_does_not_contain_sample():
    test_instrument = Instrument()
    dictionary_output = test_instrument.as_dict()

    child_names = [child["name"] for child in dictionary_output["children"]]
    assert (
        SAMPLE_NAME not in child_names
    ), "Sample component should be in NXentry not in NXinstrument"


def test_instrument_as_dict_contains_components():
    test_instrument = Instrument()
    component_list = test_instrument.get_component_list()
    zeroth_test_component_name = "Component_A"
    first_test_component_name = "Component_B"
    component_list.append(Component(zeroth_test_component_name, []))
    component_list.append(Component(first_test_component_name, []))
    dictionary_output = test_instrument.as_dict()

    child_names = [child["name"] for child in dictionary_output["children"]]
    assert zeroth_test_component_name in child_names
    assert first_test_component_name in child_names
