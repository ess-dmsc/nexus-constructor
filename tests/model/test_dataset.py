from nexus_constructor.model.dataset import Dataset


def test_dataset_as_dict_contains_expected_keys():
    input_name = "test_dataset"
    test_dataset = Dataset(
        name=input_name, size="[1]", type="String", values="the_value"
    )
    dictionary_output = test_dataset.as_dict()
    for expected_key in ("name", "type"):
        assert expected_key in dictionary_output.keys()

    assert dictionary_output["name"] == input_name
