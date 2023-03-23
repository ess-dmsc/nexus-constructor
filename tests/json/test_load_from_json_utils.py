import pytest

from nexus_constructor.json.load_from_json_utils import _find_nx_class


@pytest.mark.parametrize("class_attribute", [[{"name": "NX_class"}], [{"name": "123"}]])
def test_GIVEN_no_nx_class_values_for_component_WHEN_loading_from_json_THEN_json_loader_returns_false(
    class_attribute,
):
    assert not _find_nx_class(class_attribute)


@pytest.mark.parametrize(
    "class_attribute",
    [[{"name": "NX_class", "values": "NXmonitor"}], [{"NX_class": "NXmonitor"}]],
)
def test_GIVEN_nx_class_in_different_formats_WHEN_reading_class_information_THEN_read_nx_class_recognises_both_formats(
    class_attribute,
):
    assert _find_nx_class(class_attribute) == "NXmonitor"
