from nexus_constructor.model.dataset import Dataset, DatasetMetadata


def test_dataset_as_dict_contains_expected_keys():
    test_dataset_metadata = DatasetMetadata("String", (0,))
    input_name = "test_dataset"
    test_dataset = Dataset(input_name, test_dataset_metadata, "the_value")
    dictionary_output = test_dataset.as_dict()
    for expected_key in ("name", "type"):
        assert expected_key in dictionary_output.keys()

    assert dictionary_output["name"] == input_name
