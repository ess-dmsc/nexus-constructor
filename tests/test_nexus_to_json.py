import io
import json

import numpy as np

from nexus_constructor.nexus_filewriter_json.writer import (
    NexusToDictConverter,
    create_writer_commands,
    object_to_json_file,
)
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

    assert size == expected_size
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

    assert size == expected_size
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

    assert size == expected_size
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


def test_GIVEN_single_value_WHEN_handling_dataset_THEN_size_field_does_not_exist_in_root_dict():
    file = create_in_memory_file("test5")

    dataset_name = "test_ds"
    dataset_value = 1.1
    dataset_dtype = np.float

    dataset = file.create_dataset(dataset_name, data=dataset_value, dtype=dataset_dtype)
    dataset.attrs["NX_class"] = "NXpinhole"

    converter = NexusToDictConverter()
    root_dict = converter.convert(file, [], [])

    ds = root_dict["children"][0]

    assert ds["name"].lstrip("/") == dataset_name
    assert ds["type"] == "dataset"
    assert ds["values"] == dataset_value
    assert "size" not in ds["dataset"]


def test_GIVEN_multiple_values_WHEN_handling_dataset_THEN_size_field_does_exist_in_root_dict():
    file = create_in_memory_file("test6")

    dataset_name = "test_ds"
    dataset_value = [1.1, 1.2, 1.3]
    dataset_dtype = np.float

    dataset = file.create_dataset(dataset_name, data=dataset_value, dtype=dataset_dtype)
    dataset.attrs["NX_class"] = "NXpinhole"

    converter = NexusToDictConverter()
    root_dict = converter.convert(file, [], [])
    ds = root_dict["children"][0]

    assert ds["name"].lstrip("/") == dataset_name
    assert ds["type"] == "dataset"
    assert ds["values"] == dataset_value
    assert ds["dataset"]["size"] == (len(dataset_value),)


def test_GIVEN_stream_in_group_children_WHEN_handling_group_THEN_stream_is_appended_to_children():
    file = create_in_memory_file("test7")
    group_name = "test_group"
    group = file.create_group(group_name)
    group.attrs["NX_class"] = "NXgroup"

    group_contents = ["test_contents_item"]

    converter = NexusToDictConverter()
    root_dict = converter.convert(
        file, streams={f"/{group_name}": group_contents}, links=[]
    )

    assert group.name == root_dict["children"][0]["name"]
    assert group_contents == root_dict["children"][0]["children"][0]["stream"]


def test_GIVEN_link_in_group_children_WHEN_handling_group_THEN_link_is_appended_to_children():
    file = create_in_memory_file("test7")
    group_name = "test_group"
    group = file.create_group(group_name)
    group.attrs["NX_class"] = "NXgroup"

    group_to_be_linked_name = "test_linked_group"
    group_to_be_linked = file.create_group(group_to_be_linked_name)
    group_to_be_linked.attrs["NX_class"] = "NXgroup"

    link_name = "testlink"

    group_contents = {"name": link_name, "target": group_to_be_linked.name}

    converter = NexusToDictConverter()
    root_dict = converter.convert(file, streams={}, links={group.name: group_contents})

    assert group.name == root_dict["children"][0]["name"]

    link_dict = root_dict["children"][0]["children"][0]
    assert "link" == link_dict["type"]
    assert link_name == link_dict["name"]
    assert group_to_be_linked.name == link_dict["target"]


def test_GIVEN_start_time_WHEN_creating_writercommands_THEN_start_time_is_included_in_command():
    start_time = 123413425
    start_cmd, _ = create_writer_commands({}, "", start_time=start_time)
    assert start_cmd["start_time"] == start_time


def test_GIVEN_stop_time_WHEN_creating_writer_commands_THEN_stop_time_is_included_in_command():
    stop_time = 123231412
    _, stop_cmd = create_writer_commands({}, "", stop_time=stop_time)
    assert stop_cmd["stop_time"] == stop_time


def test_GIVEN_no_job_id_WHEN_creating_writer_commands_THEN_job_id_is_auto_generated():
    start_cmd, stop_cmd = create_writer_commands({}, "")
    assert start_cmd["job_id"]
    assert stop_cmd["job_id"]


def test_GIVEN_job_id_WHEN_creating_writer_commands_THEN_job_id_is_present_in_commands():
    job_id = "something"
    start_cmd, stop_cmd = create_writer_commands({}, "", job_id=job_id)
    assert start_cmd["job_id"] == job_id
    assert stop_cmd["job_id"] == job_id


def test_GIVEN_output_file_WHEN_creating_writer_commands_THEN_output_file_is_present_in_write_command():
    filename = "test.nxs"
    start_cmd, _ = create_writer_commands({}, output_filename=filename)

    assert start_cmd["file_attributes"]["file_name"] == filename


def test_GIVEN_nexus_object_and_fake_fileIO_WHEN_calling_object_to_json_file_THEN_fileIO_contains_nexus_object_attributes():
    file = io.StringIO(newline=None)

    tree = {"test": ["index1", "index2"]}
    object_to_json_file(tree, file)
    file.flush()

    assert json.loads(file.getvalue()) == tree
