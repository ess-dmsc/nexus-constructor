from nexus_constructor.model.user import User


def test_can_get_values_dict():
    user_data = {
        "name": "John Smith",
        "email": "js@ess.eu",
        "facility_user_id": "js90",
        "affiliation": "ESS",
    }
    test_user = User(**user_data)

    result = test_user.values_dict()

    assert result == user_data


def test_if_nexus_name_not_specified_then_is_generated():
    user_data = {
        "name": "John Smith",
        "email": "js@ess.eu",
        "facility_user_id": "js90",
        "affiliation": "ESS",
    }
    test_user = User(**user_data)

    assert test_user.name == "user_JohnSmith"


def test_nexus_name_is_specified():
    user_data = {
        "name": "John Smith",
        "email": "js@ess.eu",
        "facility_user_id": "js90",
        "affiliation": "ESS",
    }
    test_user = User("user_123", **user_data)

    assert test_user.name == "user_123"


def extract_children_name_value(dictionary):
    children = {}
    for child in dictionary["children"]:
        if "config" in child:
            children[child["config"]["name"]] = child["config"]["values"]
    return children


def test_as_dict_contains_all_data():
    user_data = {
        "name": "John Smith",
        "email": "js@ess.eu",
        "facility_user_id": "js90",
        "affiliation": "ESS",
    }
    test_user = User(**user_data)

    result = test_user.as_dict([])

    assert extract_children_name_value(result) == user_data
