from nexus_constructor.json.load_from_json import _retrieve_children_list
from nexus_constructor.json.load_from_json_utils import _read_nx_class


def test_GIVEN_unable_to_find_nexus_structure_field_WHEN_loading_from_json_THEN_json_loader_returns_false(
    nexus_json_dictionary,
):

    del nexus_json_dictionary["nexus_structure"]
    assert not _retrieve_children_list(nexus_json_dictionary)


def test_GIVEN_unable_to_find_first_children_field_WHEN_loading_from_json_THEN_json_loader_returns_false(
    nexus_json_dictionary,
):

    del nexus_json_dictionary["nexus_structure"]["children"]
    assert not _retrieve_children_list(nexus_json_dictionary)


def test_GIVEN_unable_to_find_second_children_field_WHEN_loading_from_json_THEN_json_loader_returns_false(
    nexus_json_dictionary,
):

    del nexus_json_dictionary["nexus_structure"]["children"][0]["children"]
    assert not _retrieve_children_list(nexus_json_dictionary)


@pytest.mark.parametrize("class_attribute", [[{"name": "NX_class"}], [{"name": "123"}]])
def test_GIVEN_no_nx_class_values_for_component_WHEN_loading_from_json_THEN_json_loader_returns_false(
    class_attribute,
):
    assert not _read_nx_class(class_attribute)

@pytest.mark.parametrize(
    "class_attribute",
    [[{"name": "NX_class", "values": "NXmonitor"}], [{"NX_class": "NXmonitor"}]],
)
def test_GIVEN_nx_class_in_different_formats_WHEN_reading_class_information_THEN_read_nx_class_recognises_both_formats(
    class_attribute,
):

    assert _read_nx_class(class_attribute) == "NXmonitor"