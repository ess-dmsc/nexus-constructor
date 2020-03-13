import io
import json
from ast import literal_eval
import numpy as np
import h5py
import pytest

from nexus_constructor.instrument import Instrument
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.json.filewriter_json_writer import (
    NexusToDictConverter,
    write_nexus_structure_to_json,
    _add_attributes,
    ATTR_NAME_BLACKLIST,
    get_data_and_type,
)
from nexus_constructor.json.helpers import object_to_json_file
from nexus_constructor.json.forwarder_json_writer import generate_forwarder_command
from tests.test_utils import NX_CLASS_DEFINITIONS


def test_GIVEN_float32_WHEN_getting_data_and_dtype_THEN_function_returns_correct_fw_json_dtype(
    file,
):
    expected_dtype = "float"
    expected_size = 1
    expected_value = np.float(1.1)

    dataset = file.create_dataset("test_dataset", dtype="float32", data=expected_value)

    data, dtype, size = get_data_and_type(dataset)

    assert size == expected_size
    assert dtype == expected_dtype
    assert np.isclose(data, expected_value)


def test_GIVEN_float64_WHEN_getting_data_and_dtype_THEN_function_returns_correct_fw_json_dtype(
    file,
):
    expected_dtype = "double"
    expected_size = 1
    expected_value = np.float64(324.123_231_413_515_223_412_352_135_34)

    dataset = file.create_dataset("test_dataset", dtype=np.float64, data=expected_value)

    data, dtype, size = get_data_and_type(dataset)

    assert size == expected_size
    assert dtype == expected_dtype
    assert data == expected_value


def test_GIVEN_int32_WHEN_getting_data_and_dtype_THEN_function_returns_correct_fw_json_dtype(
    file,
):
    expected_dtype = "int32"
    expected_size = 1
    expected_value = np.int32(42)

    dataset = file.create_dataset("test_dataset", dtype="int32", data=expected_value)

    data, dtype, size = get_data_and_type(dataset)

    assert size == expected_size
    assert dtype == expected_dtype
    assert data == expected_value


def test_GIVEN_int64_WHEN_getting_data_and_dtype_THEN_function_returns_correct_fw_json_dtype(
    file,
):
    expected_dtype = "int64"
    expected_size = 1
    expected_value = np.int64(171_798_691_842)  # bigger than max 32b int

    dataset = file.create_dataset("test_dataset", dtype="int64", data=expected_value)

    data, dtype, size = get_data_and_type(dataset)

    assert size == expected_size
    assert dtype == expected_dtype
    assert data == expected_value


def test_GIVEN_single_string_WHEN_getting_data_and_dtype_THEN_function_returns_correct_fw_json_dtype(
    file,
):
    expected_dtype = "string"
    expected_size = 1
    expected_value = np.string_("udder")

    dataset = file.create_dataset("test_dataset", data=expected_value, dtype="S5")

    data, dtype, size = get_data_and_type(dataset)

    assert size == expected_size
    assert dtype == expected_dtype
    assert bytes(data, "ASCII") == expected_value


def test_GIVEN_array_WHEN_getting_data_and_dtype_THEN_function_returns_correcte_fw_json_dtype_and_values(
    file,
):
    expected_dtype = "float"
    expected_values = [1.1, 1.2, 1.3]

    dataset = file.create_dataset("test_dataset", data=expected_values, dtype="float32")
    data, dtype, size = get_data_and_type(dataset)

    assert size == (len(expected_values),)
    assert np.allclose(data, expected_values)
    assert dtype == expected_dtype


def test_GIVEN_nx_class_and_attributes_are_bytes_WHEN_output_to_json_THEN_they_are_written_as_utf8(
    file,
):
    dataset_name = "test_ds"
    dataset_value = 1
    dataset_dtype = np.int32

    dataset = file.create_dataset(dataset_name, data=dataset_value, dtype=dataset_dtype)
    test_nx_class = b"NXpinhole"
    test_string_attr = b"some_string"
    dataset.attrs["NX_class"] = test_nx_class
    dataset.attrs["string_attr"] = test_string_attr

    converter = NexusToDictConverter()
    root_dict = converter.convert(file)

    ds = root_dict["children"][0]

    for attribute in ds["attributes"]:
        assert attribute["name"] in ["NX_class", "string_attr"]
        if attribute["name"] == "NX_class":
            assert attribute["values"] == test_nx_class.decode("utf8")
        elif attribute["name"] == "string_attr":
            assert attribute["values"] == test_string_attr.decode("utf8")


@pytest.mark.parametrize("test_input", [42, 4.2, "test"])
def test_GIVEN_dataset_with_an_attribute_WHEN_output_to_json_THEN_attribute_is_present_in_json(
    file, test_input
):
    dataset_name = "test_ds"
    dataset_value = 1
    dataset_dtype = np.int32

    dataset = file.create_dataset(dataset_name, data=dataset_value, dtype=dataset_dtype)
    test_attr_name = "test_attr"
    dataset.attrs[test_attr_name] = test_input

    converter = NexusToDictConverter()
    root_dict = converter.convert(file)

    ds = root_dict["children"][0]

    assert ds["attributes"][0]["name"] == test_attr_name
    assert ds["attributes"][0]["values"] == test_input


@pytest.mark.parametrize("test_input", [[1, 2, 3], [1.1, 2.2, 3.3]])
def test_GIVEN_dataset_with_an_array_attribute_WHEN_output_to_json_THEN_attribute_is_present_in_json(
    file, test_input
):
    dataset_name = "test_ds"
    dataset_value = 1
    dataset_dtype = np.int32

    dataset = file.create_dataset(dataset_name, data=dataset_value, dtype=dataset_dtype)
    test_attr_name = "test_attr"
    dataset.attrs[test_attr_name] = test_input

    converter = NexusToDictConverter()
    root_dict = converter.convert(file)

    ds = root_dict["children"][0]

    assert ds["attributes"][0]["name"] == test_attr_name
    assert ds["attributes"][0]["values"].tolist() == test_input


def test_GIVEN_single_value_WHEN_handling_dataset_THEN_size_field_does_not_exist_in_root_dict(
    file,
):
    dataset_name = "test_ds"
    dataset_value = 1.1
    dataset_dtype = np.float

    dataset = file.create_dataset(dataset_name, data=dataset_value, dtype=dataset_dtype)
    dataset.attrs["NX_class"] = "NXpinhole"

    converter = NexusToDictConverter()
    root_dict = converter.convert(file)

    ds = root_dict["children"][0]

    assert ds["name"].lstrip("/") == dataset_name
    assert ds["type"] == "dataset"
    assert ds["values"] == dataset_value
    assert "size" not in ds["dataset"]


def test_GIVEN_multiple_values_WHEN_handling_dataset_THEN_size_field_does_exist_in_root_dict(
    file,
):
    dataset_name = "test_ds"
    dataset_value = [1.1, 1.2, 1.3]
    dataset_dtype = np.float

    dataset = file.create_dataset(dataset_name, data=dataset_value, dtype=dataset_dtype)
    dataset.attrs["NX_class"] = "NXpinhole"

    converter = NexusToDictConverter()
    root_dict = converter.convert(file)
    ds = root_dict["children"][0]

    assert ds["name"].lstrip("/") == dataset_name
    assert ds["type"] == "dataset"
    assert ds["values"] == dataset_value
    assert ds["dataset"]["size"] == (len(dataset_value),)


def test_GIVEN_stream_in_group_children_WHEN_handling_group_THEN_stream_is_appended_to_children(
    file,
):
    group_name = "test_group"
    group = file.create_group(group_name)
    group.attrs["NX_class"] = "NCstream"

    group_contents = {
        "writer_module": "f142",
        "topic": "topic1",
        "source": "SIMPLE:DOUBLE",
        "type": "double",
        "value_units": "cubits",
        "array_size": 32,
    }

    for name, value in group_contents.items():
        group.create_dataset(name, data=value)

    converter = NexusToDictConverter()
    root_dict = converter.convert(file)

    assert len(root_dict["children"]) == 1, "The stream group has been omitted"
    assert group_name == root_dict["children"][0]["name"]
    assert group_contents == root_dict["children"][0]["children"][0]["stream"]
    assert "attributes" not in root_dict["children"][0]


def test_GIVEN_link_in_group_children_WHEN_handling_group_THEN_link_is_appended_to_children(
    file,
):
    root_group = file.create_group("root")

    group_to_be_linked_name = "test_linked_group"
    group_to_be_linked = root_group.create_group(group_to_be_linked_name)
    group_to_be_linked.attrs["NX_class"] = "NXgroup"

    group_name = "test_group_with_link"
    root_group[group_name] = h5py.SoftLink(group_to_be_linked.name)
    root_group[group_name].attrs["NX_class"] = "NXgroup"

    converter = NexusToDictConverter()
    root_dict = converter.convert(file)

    assert len(root_dict["children"]) == 1, "The link group has been omitted"
    assert root_dict["children"][0]["children"][0]["type"] == "link"
    assert (
        root_group[group_name].name.split("/")[-1]
        == root_dict["children"][0]["children"][0]["name"]
    )
    assert group_to_be_linked.name == root_dict["children"][0]["children"][0]["target"]


def test_GIVEN_link_in_group_children_that_is_a_dataset_WHEN_handling_group_THEN_link_is_appended_to_children(
    file,
):
    root_group = file.create_group("root")
    ds_to_be_linked_name = "test_linked_dataset"
    dataset_to_be_linked = root_group.create_dataset(ds_to_be_linked_name, data=1)
    dataset_to_be_linked.attrs["NX_class"] = "NXgroup"

    group_name = "test_group_with_link"
    root_group[group_name] = h5py.SoftLink(dataset_to_be_linked.name)
    root_group[group_name].attrs["NX_class"] = "NXgroup"

    converter = NexusToDictConverter()
    root_dict = converter.convert(file)

    assert root_dict["children"][0]["children"][0]["type"] == "link"
    assert (
        root_group[group_name].name.split("/")[-1]
        == root_dict["children"][0]["children"][0]["name"]
    )
    assert (
        dataset_to_be_linked.name == root_dict["children"][0]["children"][0]["target"]
    )


def test_GIVEN_group_with_multiple_attributes_WHEN_converting_nexus_to_dict_THEN_attributes_end_up_in_file(
    file,
):
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
    root_dict = converter.convert(file)

    assert group.name.split("/")[-1] == root_dict["children"][0]["name"]

    assert field1.name.split("/")[-1] == root_dict["children"][0]["children"][0]["name"]
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

    assert field2.name.split("/")[-1] == root_dict["children"][0]["children"][1]["name"]
    assert field2value == root_dict["children"][0]["children"][1]["values"]


def test_GIVEN_nexus_object_and_fake_fileIO_WHEN_calling_object_to_json_file_THEN_fileIO_contains_nexus_object_attributes():
    file = io.StringIO(newline=None)

    tree = {"test": ["index1", "index2"]}
    object_to_json_file(tree, file)
    file.flush()

    assert json.loads(file.getvalue()) == tree


def test_GIVEN_instrument_containing_component_WHEN_generating_json_THEN_file_is_written_containing_components():
    file = io.StringIO(newline=None)
    wrapper = NexusWrapper("test.nxs")
    data = Instrument(wrapper, NX_CLASS_DEFINITIONS)

    component_name = "pinhole"
    component_nx_class = "NXpinhole"

    dataset_name = "depends_on"
    dataset_value = "something_else"

    component = data.create_component(component_name, component_nx_class, "")
    component.set_field(dataset_name, value=dataset_value, dtype=str)

    write_nexus_structure_to_json(data, file)

    output_file_dict = json.loads(file.getvalue())

    component = output_file_dict["children"][0]["children"][0]["children"][0]

    assert component["name"].lstrip("/entry/instrument/") == component_name
    assert (
        component["children"][0]["name"].lstrip(f"/entry/instrument/{component_name}/")
        == dataset_name
    )
    assert component["children"][0]["type"] == "dataset"
    assert component["children"][0]["values"] == dataset_value
    assert component["children"][0]["dataset"]["type"] == "string"


def test_GIVEN_float64_WHEN_getting_data_and_type_THEN_returns_correct_dtype(file):
    dataset_name = "ds"
    dataset_type = np.float64
    dataset_value = np.float64(2.123)

    dataset = file.create_dataset(dataset_name, dtype=dataset_type, data=dataset_value)
    data, dtype, size = get_data_and_type(dataset)

    assert data == dataset_value
    assert dtype == "double"
    assert size == 1


def test_GIVEN_float_WHEN_getting_data_and_type_THEN_returns_correct_dtype(file):
    dataset_name = "ds"
    dataset_type = np.float32
    dataset_value = np.float32(2.123)

    dataset = file.create_dataset(dataset_name, dtype=dataset_type, data=dataset_value)
    data, dtype, size = get_data_and_type(dataset)

    assert data == dataset_value
    assert dtype == "float"
    assert size == 1


def test_GIVEN_string_list_WHEN_getting_data_and_type_THEN_returns_correct_dtype(file):
    dataset_name = "ds"
    dataset_value = np.string_(["s", "t", "r"])

    dataset = file.create_dataset(dataset_name, data=dataset_value)

    data, dtype, size = get_data_and_type(dataset)

    assert data == [x.decode("ASCII") for x in list(dataset_value)]
    assert size == (len(dataset_value),)


def test_GIVEN_stream_with_no_forwarder_streams_WHEN_generating_forwarder_command_THEN_output_does_not_contain_any_pvs(
    file,
):
    group_name = "test_group"
    group = file.create_group(group_name)
    group.attrs["NX_class"] = "NCstream"

    group.create_dataset("writer_module", data="ev42")
    group.create_dataset("source", data="source1")
    group.create_dataset("topic", data="topic1")

    dummy_file = io.StringIO()

    generate_forwarder_command(dummy_file, file, "ca", "")

    assert not literal_eval(dummy_file.getvalue())["streams"]


def test_GIVEN_stream_with_f142_command_WHEN_generating_forwarder_command_THEN_output_contains_pv(
    file,
):
    pv_name = "pv1"
    topic = "someTopic"
    writer_module = "f142"
    group_name = "test_group"
    group = file.create_group(group_name)
    group.attrs["NX_class"] = "NCstream"

    group.create_dataset("writer_module", data=writer_module)
    group.create_dataset("topic", data=topic)
    group.create_dataset("source", data=pv_name)

    dummy_file = io.StringIO()

    generate_forwarder_command(dummy_file, file, "ca", "")

    streams_ = literal_eval(dummy_file.getvalue())["streams"]
    assert len(streams_) == 1
    assert streams_[0]["channel"] == pv_name
    assert streams_[0]["converter"]["topic"] == topic
    assert streams_[0]["converter"]["schema"] == writer_module


def test_GIVEN_stream_with_f142_command_and_non_forwarder_modules_THEN_only_f142_is_contained(
    file,
):

    group = file.create_group("test_group")
    group.attrs["NX_class"] = "NCstream"

    group.create_dataset("writer_module", data="ev42")
    group.create_dataset("source", data="source1")
    group.create_dataset("topic", data="topic1")

    group2 = file.create_group("test_group2")
    group2.attrs["NX_class"] = "NCstream"

    pv_name = "pv1"
    topic = "localhost:9092/someTopic"
    writer_module = "f142"
    group2.create_dataset("writer_module", data=writer_module)
    group2.create_dataset("topic", data=topic)
    group2.create_dataset("source", data=pv_name)

    dummy_file = io.StringIO()

    generate_forwarder_command(dummy_file, file, "ca", "")

    streams_ = literal_eval(dummy_file.getvalue())["streams"]
    assert len(streams_) == 1
    assert streams_[0]["channel"] == pv_name
    assert streams_[0]["converter"]["topic"] == topic
    assert streams_[0]["converter"]["schema"] == writer_module


def test_GIVEN_stream_with_tdc_command_WHEN_generating_forwarder_command_THEN_output_contains_pv(
    file,
):
    pv_name = "tdcpv1"
    topic = "localhost:9092/someOtherTopic"
    writer_module = "TdcTime"

    group_name = "test_group"
    group = file.create_group(group_name)
    group.attrs["NX_class"] = "NCstream"

    group.create_dataset("writer_module", data=writer_module)
    group.create_dataset("topic", data=topic)
    group.create_dataset("source", data=pv_name)

    dummy_file = io.StringIO()

    generate_forwarder_command(dummy_file, file, "pva", "")

    streams_ = literal_eval(dummy_file.getvalue())["streams"]
    assert len(streams_) == 1
    assert streams_[0]["channel"] == pv_name
    assert streams_[0]["converter"]["topic"] == topic
    assert streams_[0]["converter"]["schema"] == writer_module


def test_GIVEN_stream_with_one_pv_with_two_topics_WHEN_generating_forwarder_command_THEN_contains_one_converter_with_list(
    file,
):
    pv_name = "testPV"

    topic1 = "topic1"
    topic2 = "topic2"

    writer_module = "f142"

    group = file.create_group("test_group")
    group.attrs["NX_class"] = "NCstream"
    group.create_dataset("writer_module", data=writer_module)
    group.create_dataset("source", data=pv_name)
    group.create_dataset("topic", data=topic1)

    group2 = file.create_group("test_group2")
    group2.attrs["NX_class"] = "NCstream"
    group2.create_dataset("writer_module", data=writer_module)
    group2.create_dataset("topic", data=topic2)
    group2.create_dataset("source", data=pv_name)

    dummy_file = io.StringIO()

    generate_forwarder_command(dummy_file, file, "ca", "")

    streams_ = literal_eval(dummy_file.getvalue())["streams"]

    assert len(streams_) == 1

    assert isinstance(streams_[0]["converter"], list)
    assert streams_[0]["channel"] == pv_name
    assert streams_[0]["converter"][0]["topic"] == topic1
    assert streams_[0]["converter"][1]["topic"] == topic2


def test_GIVEN_stream_with_pv_forwarding_to_three_topics_WHEN_generating_forwarder_command_THEN_stream_is_added_to_converters(
    file,
):
    pv_name = "testPV"

    topic1 = "topic1"
    topic2 = "topic2"
    topic3 = "topic3"

    writer_module = "f142"

    group = file.create_group("test_group")
    group.attrs["NX_class"] = "NCstream"
    group.create_dataset("writer_module", data=writer_module)
    group.create_dataset("source", data=pv_name)
    group.create_dataset("topic", data=topic1)

    group2 = file.create_group("test_group2")
    group2.attrs["NX_class"] = "NCstream"
    group2.create_dataset("writer_module", data=writer_module)
    group2.create_dataset("topic", data=topic2)
    group2.create_dataset("source", data=pv_name)

    group3 = file.create_group("test_group3")
    group3.attrs["NX_class"] = "NCstream"
    group3.create_dataset("writer_module", data=writer_module)
    group3.create_dataset("topic", data=topic3)
    group3.create_dataset("source", data=pv_name)

    dummy_file = io.StringIO()

    generate_forwarder_command(dummy_file, file, "pva", "")

    streams_ = literal_eval(dummy_file.getvalue())["streams"]

    assert len(streams_) == 1

    assert isinstance(streams_[0]["converter"], list)
    assert streams_[0]["channel"] == pv_name
    assert streams_[0]["converter"][0]["topic"] == topic1
    assert streams_[0]["converter"][1]["topic"] == topic2
    assert streams_[0]["converter"][2]["topic"] == topic3


def test_GIVEN_stream_with_topic_that_includes_broker_and_default_broker_provided_WHEN_generating_forwarder_command_THEN_default_broker_not_included(
    file,
):
    pv_name = "testPV"

    topic = "broker:9092/topic"
    writer_module = "f142"

    group = file.create_group("test_group")
    group.attrs["NX_class"] = "NCstream"
    group.create_dataset("writer_module", data=writer_module)
    group.create_dataset("source", data=pv_name)
    group.create_dataset("topic", data=topic)

    default_broker = "somedefaultbroker"

    dummy_file = io.StringIO()

    generate_forwarder_command(dummy_file, file, "pva", default_broker)

    streams_ = literal_eval(dummy_file.getvalue())["streams"]

    assert len(streams_) == 1
    assert streams_[0]["converter"]["topic"] == topic
    assert default_broker not in streams_[0]["converter"]["topic"]


def test_GIVEN_stream_with_topic_not_including_broker_and_default_broker_provided_WHEN_generating_forwarder_command_THEN_default_broker_is_included(
    file,
):
    pv_name = "testPV"

    topic = "topic1"
    writer_module = "f142"

    group = file.create_group("test_group")
    group.attrs["NX_class"] = "NCstream"
    group.create_dataset("writer_module", data=writer_module)
    group.create_dataset("source", data=pv_name)
    group.create_dataset("topic", data=topic)

    default_broker = "somedefaultbroker"

    dummy_file = io.StringIO()

    generate_forwarder_command(dummy_file, file, "pva", default_broker)

    streams_ = literal_eval(dummy_file.getvalue())["streams"]

    assert len(streams_) == 1
    assert default_broker in streams_[0]["converter"]["topic"]
    assert streams_[0]["converter"]["topic"] == default_broker + "/" + topic


def test_GIVEN_stream_with_topic_not_including_broker_and_default_broker_not_provided_WHEN_generating_forwarder_command_THEN_topic_does_not_include_broker(
    file,
):
    pv_name = "testPV"

    topic = "topic1"
    writer_module = "f142"

    group = file.create_group("test_group")
    group.attrs["NX_class"] = "NCstream"
    group.create_dataset("writer_module", data=writer_module)
    group.create_dataset("source", data=pv_name)
    group.create_dataset("topic", data=topic)

    dummy_file = io.StringIO()

    generate_forwarder_command(dummy_file, file, "pva", "")

    streams_ = literal_eval(dummy_file.getvalue())["streams"]

    assert len(streams_) == 1

    assert streams_[0]["converter"]["topic"] == topic


def test_GIVEN_no_attributes_WHEN_adding_attributes_THEN_root_dict_is_not_changed(file):
    root_dict = dict()
    dataset = file.create_dataset("test", data=123)
    assert not dataset.attrs.keys()
    _add_attributes(dataset, root_dict)
    assert not root_dict


def test_GIVEN_attribute_WHEN_adding_attributes_THEN_attrs_are_added_to_root_dict(file):
    root_dict = dict()
    dataset_name = "test"
    dataset = file.create_dataset(dataset_name, data=123)
    attr_key = "something"
    attr_value = "some_value"
    dataset.attrs[attr_key] = attr_value
    _add_attributes(dataset, root_dict)
    assert root_dict["attributes"]
    assert root_dict["attributes"][0]["name"] == attr_key
    assert root_dict["attributes"][0]["values"] == attr_value


def test_GIVEN_attribute_in_blacklist_WHEN_adding_attributes_THEN_attrs_is_blank(file):
    root_dict = dict()
    dataset_name = "test"
    dataset = file.create_dataset(dataset_name, data=123)
    attr_key = ATTR_NAME_BLACKLIST[0]
    attr_value = "some_value"
    dataset.attrs[attr_key] = attr_value
    _add_attributes(dataset, root_dict)
    assert not root_dict
