import numpy as np

from nexus_constructor.nexus_filewriter_json.writer import NexusToDictConverter
import h5py


def create_in_memory_file(filename):
    return h5py.File(filename, mode="x", driver="core", backing_store=False)


def test_GIVEN_float32_WHEN_getting_data_and_dtype_THEN_function_returns_correct_fw_json_dtype():
    expected_dtype = "float"
    expected_size = 1
    expected_value = np.float(23.11585)

    file = create_in_memory_file("test1")
    dataset = file.create_dataset("test_dataset", dtype=np.float, data=expected_value)

    converter = NexusToDictConverter()

    data, dtype, size = converter._get_data_and_type(dataset)

    assert size == 1
    assert dtype == expected_dtype
    assert data == expected_value


def test_GIVEN_float64_WHEN_getting_data_and_dtype_THEN_function_returns_correct_fw_json_dtype():
    expected_dtype = "double"
    expected_size = 1
    expected_value = np.float64(324.12323141351522341235213534)

    file = create_in_memory_file("test2")
    dataset = file.create_dataset("test_dataset", dtype=np.float64, data=expected_value)

    converter = NexusToDictConverter()

    data, dtype, size = converter._get_data_and_type(dataset)

    assert size == 1
    assert dtype == expected_dtype
    assert data == expected_value


def test_GIVEN_single_string_WHEN_getting_data_and_dtype_THEN_function_returns_correct_fw_json_dtype():
    expected_dtype = "string"
    expected_size = 1
    expected_value = np.string_("udder")

    file = create_in_memory_file("test3")
    dataset = file.create_dataset("test_dataset", data=expected_value, dtype="S5")

    converter = NexusToDictConverter()

    data, dtype, size = converter._get_data_and_type(dataset)

    assert size == 1
    assert dtype == expected_dtype
    assert bytes(data, "ASCII") == expected_value


def test_GIVEN_array_WHEN_getting_data_and_dtype_THEN_function_returns_correcte_fw_json_dtype_and_values():
    expected_dtype = "float"
    expected_values = [1.1, 1.2, 1.3]

    file = create_in_memory_file("test4")
    dataset = file.create_dataset("test_dataset", data=expected_values)
    converter = NexusToDictConverter()
    data, dtype, size = converter._get_data_and_type(dataset)

    assert size == (len(expected_values),)
    assert data == expected_values
    assert dtype == expected_dtype
