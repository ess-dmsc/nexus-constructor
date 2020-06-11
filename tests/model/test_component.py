from nexus_constructor.model.component import Component, TRANSFORMS_GROUP_NAME
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.model.dataset import DatasetMetadata


def test_component_as_dict_contains_transformations():
    zeroth_transform_name = "test_transform_A"
    first_transform_name = "test_transform_B"
    metadata = DatasetMetadata("String", (0,))
    test_component = Component(
        "test_component",
        [
            Transformation(zeroth_transform_name, metadata),
            Transformation(first_transform_name, metadata),
        ],
    )
    dictionary_output = test_component.as_dict()

    assert dictionary_output["children"][0]["name"] == TRANSFORMS_GROUP_NAME
    child_names = [
        child["name"] for child in dictionary_output["children"][0]["children"]
    ]
    assert zeroth_transform_name in child_names
    assert first_transform_name in child_names
