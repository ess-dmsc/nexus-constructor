import io
import json

import numpy as np

from nexus_constructor.instrument import Instrument
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.nexus_filewriter_json.writer import (
    NexusToDictConverter,
    create_writer_commands,
    object_to_json_file,
    generate_json,
)
import h5py


def create_in_memory_file(filename):
    return h5py.File(filename, mode="x", driver="core", backing_store=False)


def test_GIVEN_float32_WHEN_getting_data_and_dtype_THEN_function_returns_correct_fw_json_dtype():
    expected_dtype = "float"
    expected_size = 1
    expected_value = np.float(1.1)

    file = create_in_memory_file("test1")
    dataset = file.create_dataset("test_dataset", dtype="float32", data=expected_value)

    converter = NexusToDictConverter()

    data, dtype, size = converter._get_data_and_type(dataset)

    assert size == expected_size
    assert dtype == expected_dtype
    assert np.isclose(data, expected_value)


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
    dataset = file.create_dataset("test_dataset", data=expected_values, dtype="float32")
    converter = NexusToDictConverter()
    data, dtype, size = converter._get_data_and_type(dataset)

    assert size == (len(expected_values),)
    assert np.allclose(data, expected_values)
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


def test_GIVEN_group_with_multiple_attributes_WHEN_converting_nexus_to_dict_THEN_attributes_end_up_in_file():
    file = create_in_memory_file("test8")

    group_name = "test_group"
    group = file.create_group(group_name)
    group.attrs["NX_class"] = "NXgroup"

    field1name = "field1"
    field1value = "field1val"

    field2name = "field2"
    field2value = 3

    arbitrary_field_name = "arbitrary_field"
    arbitrary_field_value = "something"

    field1 = group.create_dataset(field1name, data=field1value)
    field1.attrs["NX_class"] = "NXfield"
    field1.attrs[arbitrary_field_name] = arbitrary_field_value

    field2 = group.create_dataset(field2name, data=field2value)
    field2.attrs["NX_class"] = "NXfield"

    converter = NexusToDictConverter()
    root_dict = converter.convert(file, streams=dict(), links=dict())

    assert group.name == root_dict["children"][0]["name"]

    assert field1.name == root_dict["children"][0]["children"][0]["name"]
    assert field1value == root_dict["children"][0]["children"][0]["values"]
    assert (
        "NX_class" == root_dict["children"][0]["children"][0]["attributes"][0]["name"]
    )
    assert (
        field1.attrs["NX_class"]
        == root_dict["children"][0]["children"][0]["attributes"][0]["values"]
    )

    assert (
        arbitrary_field_name
        == root_dict["children"][0]["children"][0]["attributes"][1]["name"]
    )
    assert (
        field1.attrs[arbitrary_field_name]
        == root_dict["children"][0]["children"][0]["attributes"][1]["values"]
    )

    assert field2.name == root_dict["children"][0]["children"][1]["name"]
    assert field2value == root_dict["children"][0]["children"][1]["values"]


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


def test_GIVEN_instrument_containing_component_WHEN_generating_json_THEN_file_is_written_containing_components():
    file = io.StringIO(newline=None)
    wrapper = NexusWrapper("test.nxs")
    data = Instrument(wrapper)

    component_name = "pinhole"
    component_nx_class = "NXpinhole"

    dataset_name = "depends_on"
    dataset_value = "something_else"

    component = data.add_component(component_name, component_nx_class, "")
    component.set_field(dataset_name, value=dataset_value, dtype=str)

    nexus_file_name = "test.nxs"

    generate_json(data, file, nexus_file_name=nexus_file_name)

    output_file_dict = json.loads(file.getvalue())

    component = output_file_dict["nexus_structure"]["children"][0]["children"][0]

    assert component["name"].lstrip("/entry/instrument/") == component_name
    assert (
        component["children"][0]["name"].lstrip(f"/entry/instrument/{component_name}/")
        == dataset_name
    )
    assert component["children"][0]["type"] == "dataset"
    assert component["children"][0]["values"] == dataset_value
    assert component["children"][0]["dataset"]["type"] == "string"


def test_GIVEN_float64_WHEN_getting_data_and_type_THEN_returns_correct_dtype():
    file = create_in_memory_file("test10")
    dataset_name = "ds"
    dataset_type = np.float64
    dataset_value = np.float64(2.123)

    dataset = file.create_dataset(dataset_name, dtype=dataset_type, data=dataset_value)
    converter = NexusToDictConverter()
    data, dtype, size = converter._get_data_and_type(dataset)

    assert data == dataset_value
    assert dtype == "double"
    assert size == 1


def test_GIVEN_float_WHEN_getting_data_and_type_THEN_returns_correct_dtype():
    file = create_in_memory_file("test11")

    dataset_name = "ds"
    dataset_type = np.float32
    dataset_value = np.float32(2.123)

    dataset = file.create_dataset(dataset_name, dtype=dataset_type, data=dataset_value)
    converter = NexusToDictConverter()
    data, dtype, size = converter._get_data_and_type(dataset)

    assert data == dataset_value
    assert dtype == "float"
    assert size == 1


def test_GIVEN_string_list_WHEN_getting_data_and_type_THEN_returns_correct_dtype():
    file = create_in_memory_file("test12")
    dataset_name = "ds"
    dataset_value = np.string_(["s", "t", "r"])

    dataset = file.create_dataset(dataset_name, data=dataset_value)
    converter = NexusToDictConverter()

    data, dtype, size = converter._get_data_and_type(dataset)

    assert data == [x.decode("ASCII") for x in list(dataset_value)]
    assert size == (len(dataset_value),)
