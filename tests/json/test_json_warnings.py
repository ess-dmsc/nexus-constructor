import pytest

from nexus_constructor.json.json_warnings import InvalidJson, JsonWarningsContainer

JSON_WARN_CONTAINER = JsonWarningsContainer()
JSON_WARNING = InvalidJson("Invalid JSON warning")
JSON_WARN_CONTAINER.append(JSON_WARNING)
INVALID_CONTAINER_ELEMENT = "INVALID"


def test_json_warnings_container_raises_type_error_when_instantiating_with_wrong_type():
    with pytest.raises(TypeError):
        JsonWarningsContainer([INVALID_CONTAINER_ELEMENT])


def test_json_warning_container_is_correctly_instantiated_when_providing_correct_other_container():
    this_container = JsonWarningsContainer(JSON_WARN_CONTAINER)
    assert this_container


def test_json_warning_container_is_correctly_instantiated_when_providing_warning():
    this_container = JsonWarningsContainer(JSON_WARNING)
    assert this_container


def test_json_warning_container_raises_type_error_if_appending_item_of_invalid_type():
    with pytest.raises(TypeError):
        JSON_WARN_CONTAINER.append(INVALID_CONTAINER_ELEMENT)


def test_json_warning_container_when_appending_another_container_containing_one_item():
    this_container = JsonWarningsContainer(JSON_WARNING)
    this_container.append(JSON_WARN_CONTAINER)
    assert len(this_container) == 2


def test_json_warning_container_when_using_add_operator_container():
    assert len(JSON_WARN_CONTAINER + JSON_WARN_CONTAINER + JSON_WARN_CONTAINER) == 3


def test_json_warning_container_when_using_iadd_operator_with_correct_type():
    this_container = JsonWarningsContainer(JSON_WARN_CONTAINER)
    this_container += JsonWarningsContainer(JSON_WARNING)
    assert len(this_container) == 2


def test_json_warning_container_if_using_iadd_operator_with_another_empty_json_warning_container():
    this_container = JsonWarningsContainer(JSON_WARN_CONTAINER)
    this_container += JsonWarningsContainer()
    assert len(this_container) == 1


def test_json_warning_container_when_using_add_operator_with_incorrect_type():
    with pytest.raises(TypeError):
        JSON_WARN_CONTAINER + INVALID_CONTAINER_ELEMENT


def test_json_warning_container_when_using_iadd_operator_with_incorrect_type():
    with pytest.raises(TypeError):
        this_container = JsonWarningsContainer(JSON_WARN_CONTAINER)
        this_container += INVALID_CONTAINER_ELEMENT
