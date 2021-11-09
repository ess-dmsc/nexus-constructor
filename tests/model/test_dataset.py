from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.value_type import ValueTypes


def test_dataset_as_dict_contains_expected_keys():
    input_name = "test_dataset"
    test_dataset = Dataset(
        name=input_name, size="[1]", type=ValueTypes.STRING, values="the_value"
    )
    dictionary_output = test_dataset.as_dict()
    for expected_key in ("module", "config"):
        assert expected_key in dictionary_output.keys()

    assert dictionary_output["config"]["name"] == input_name
