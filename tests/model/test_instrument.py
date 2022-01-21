from nexus_constructor.model.component import Component
from nexus_constructor.model.instrument import SAMPLE_NAME, Instrument


def test_instrument_as_dict_does_not_contain_sample():
    test_instrument = Instrument()
    dictionary_output = test_instrument.as_dict([])

    child_names = [child["name"] for child in dictionary_output["children"]]
    assert (
        SAMPLE_NAME not in child_names
    ), "Sample component should be in NXentry not in NXinstrument"


def test_instrument_as_dict_contains_components():
    test_instrument = Instrument()
    zeroth_test_component_name = "Component_A"
    first_test_component_name = "Component_B"
    test_instrument.children.append(Component(zeroth_test_component_name, []))
    test_instrument.children.append(Component(first_test_component_name, []))
    dictionary_output = test_instrument.as_dict([])

    child_names = [child["name"] for child in dictionary_output["children"]]
    assert zeroth_test_component_name in child_names
    assert first_test_component_name in child_names
