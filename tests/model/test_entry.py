from nexus_constructor.common_attrs import NX_USER, CommonAttrs
from nexus_constructor.model.entry import (
    EXP_ID_PLACEHOLDER_VALUE,
    NEXUS_EXP_ID_NAME,
    NEXUS_TITLE_NAME,
    TITLE_PLACEHOLDER_VALUE,
    USERS_PLACEHOLDER,
    Entry,
)


def find_child_dataset_by_name(dictionary, name):
    for child in dictionary["children"]:
        if child.get("module", "") == "dataset" and child["config"]["name"] == name:
            return child
    return None


def extract_based_on_nx_class(dictionary, nx_class):
    result = []
    for child in dictionary["children"]:
        if "attributes" in child:
            for attribute in child["attributes"]:
                name = attribute.get("name", "")
                if name == CommonAttrs.NX_CLASS:
                    if attribute.get("values", "") == nx_class:
                        result.append(child)
    return result


def assert_matching_datasets_exist(dictionary, expected_values):
    for name, value in expected_values.items():
        ds = find_child_dataset_by_name(dictionary, name)
        if not ds["config"]["values"] == value:
            assert (
                False
            ), f"Could not find expected_value ({value}) for dataset name ({name})"
    assert True


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

    assert find_child_dataset_by_name(dictionary, NEXUS_EXP_ID_NAME) is None


def test_blank_proposal_id_is_not_in_dictionary_after_clearing():
    test_entry = Entry()
    test_entry.proposal_id = ("MY_PROP_ID", False)
    test_entry.proposal_id = ("", False)

    dictionary = test_entry.as_dict([])

    assert find_child_dataset_by_name(dictionary, NEXUS_EXP_ID_NAME) is None


def test_defined_proposal_id_is_in_dictionary():
    test_entry = Entry()
    test_entry.proposal_id = ("MY_PROP_ID", False)

    dictionary = test_entry.as_dict([])

    result = find_child_dataset_by_name(dictionary, NEXUS_EXP_ID_NAME)
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

    assert find_child_dataset_by_name(dictionary, NEXUS_TITLE_NAME) is None


def test_blank_title_is_not_in_dictionary_after_clearing():
    test_entry = Entry()
    test_entry.title = ("MY_TITLE", False)
    test_entry.title = ("", False)

    dictionary = test_entry.as_dict([])

    assert find_child_dataset_by_name(dictionary, NEXUS_TITLE_NAME) is None


def test_defined_title_is_in_dictionary():
    test_entry = Entry()
    test_entry.title = ("MY_TITLE", False)

    dictionary = test_entry.as_dict([])

    result = find_child_dataset_by_name(dictionary, NEXUS_TITLE_NAME)
    assert result is not None
    assert result["config"]["values"] == "MY_TITLE"


def test_users_is_initially_empty():
    test_entry = Entry()

    assert len(test_entry.users) == 0


def test_users_can_be_edited_using_simple_dict_representation():
    user_john = {
        "name": "John Smith",
        "email": "js@ess.eu",
        "facility_user_id": "js90",
        "affiliation": "ESS",
    }
    test_entry = Entry()

    test_entry.users = [user_john]

    assert test_entry.users == [user_john]


def test_users_are_in_dictionary():
    user_john = {
        "name": "John Smith",
        "email": "js@ess.eu",
        "facility_user_id": "js90",
        "affiliation": "ESS",
    }

    user_betty = {
        "name": "Betty Boo",
        "email": "bb@doing.the.do",
        "facility_user_id": "bb70",
        "affiliation": "She Rockers",
    }

    test_entry = Entry()
    test_entry.users = [user_john, user_betty]

    dictionary = test_entry.as_dict([])
    result = extract_based_on_nx_class(dictionary, NX_USER)

    assert_matching_datasets_exist(result[0], user_john)
    assert_matching_datasets_exist(result[1], user_betty)


def test_if_placeholder_used_then_users_replaced_by_placeholder():
    user_john = {
        "name": "John Smith",
        "email": "js@ess.eu",
        "facility_user_id": "js90",
        "affiliation": "ESS",
    }

    test_entry = Entry()
    test_entry.users = [user_john]

    test_entry.users_placeholder = True
    dictionary = test_entry.as_dict([])

    assert len(extract_based_on_nx_class(dictionary, NX_USER)) == 0
    assert USERS_PLACEHOLDER in dictionary["children"]
