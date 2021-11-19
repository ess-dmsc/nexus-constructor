from nexus_constructor.common_attrs import INSTRUMENT_NAME
from nexus_constructor.model.entry import (
    Entry,
    EXP_ID_PLACEHOLDER_VALUE,
    NEXUS_EXP_ID_NAME,
    TITLE_PLACEHOLDER_VALUE,
    NEXUS_TITLE_NAME,
)
from nexus_constructor.model.instrument import SAMPLE_NAME, Instrument


def find_in_dict(dictionary, name):
    for child in dictionary["children"]:
        if "config" in child and child["config"]["name"] == name:
            return child
    return None


def test_entry_as_dict_contains_sample_and_instrument():
    test_entry = Entry()
    test_entry.instrument = Instrument()
    dictionary_output = test_entry.as_dict([])

    child_names = [child["name"] for child in dictionary_output["children"]]
    assert SAMPLE_NAME in child_names
    assert INSTRUMENT_NAME in child_names


def test_proposal_id_is_initially_empty():
    test_entry = Entry()

    assert test_entry.proposal_id == ("", False)


def test_proposal_id_is_set_to_use_placeholder():
    test_entry = Entry()

    test_entry.proposal_id = ("will be ignored", True)

    assert test_entry.proposal_id == (EXP_ID_PLACEHOLDER_VALUE, True)


def test_proposal_id_is_set_to_custom_value():
    test_entry = Entry()

    test_entry.proposal_id = ("MY_PROP_ID", False)

    assert test_entry.proposal_id == ("MY_PROP_ID", False)


def test_blank_proposal_id_is_not_in_dictionary():
    test_entry = Entry()

    dictionary = test_entry.as_dict([])

    assert find_in_dict(dictionary, NEXUS_EXP_ID_NAME) is None


def test_blank_proposal_id_is_not_in_dictionary_after_clearing():
    test_entry = Entry()
    test_entry.proposal_id = ("MY_PROP_ID", False)
    test_entry.proposal_id = ("", False)

    dictionary = test_entry.as_dict([])

    assert find_in_dict(dictionary, NEXUS_EXP_ID_NAME) is None


def test_defined_proposal_id_is_in_dictionary():
    test_entry = Entry()
    test_entry.proposal_id = ("MY_PROP_ID", False)

    dictionary = test_entry.as_dict([])

    result = find_in_dict(dictionary, NEXUS_EXP_ID_NAME)
    assert result is not None
    assert result["config"]["values"] == "MY_PROP_ID"


def test_title_is_initially_empty():
    test_entry = Entry()

    assert test_entry.title == ("", False)


def test_title_is_set_to_use_placeholder():
    test_entry = Entry()

    test_entry.title = ("will be ignored", True)

    assert test_entry.title == (TITLE_PLACEHOLDER_VALUE, True)


def test_title_is_set_to_custom_value():
    test_entry = Entry()

    test_entry.title = ("MY_TITLE", False)

    assert test_entry.title == ("MY_TITLE", False)


def test_blank_title_is_not_in_dictionary():
    test_entry = Entry()

    dictionary = test_entry.as_dict([])

    assert find_in_dict(dictionary, NEXUS_TITLE_NAME) is None


def test_blank_title_is_not_in_dictionary_after_clearing():
    test_entry = Entry()
    test_entry.title = ("MY_TITLE", False)
    test_entry.title = ("", False)

    dictionary = test_entry.as_dict([])

    assert find_in_dict(dictionary, NEXUS_TITLE_NAME) is None


def test_defined_title_is_in_dictionary():
    test_entry = Entry()
    test_entry.title = ("MY_TITLE", False)

    dictionary = test_entry.as_dict([])

    result = find_in_dict(dictionary, NEXUS_TITLE_NAME)
    assert result is not None
    assert result["config"]["values"] == "MY_TITLE"
