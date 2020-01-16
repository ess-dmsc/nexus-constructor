import h5py
import numpy as np
import uuid
import logging
from typing import Union, Dict, Any, List, Tuple

from nexus_constructor.instrument import Instrument
from nexus_constructor.json.helpers import object_to_json_file
from nexus_constructor.nexus.nexus_wrapper import get_nx_class, get_name_of_node

NexusObject = Union[h5py.Group, h5py.Dataset, h5py.SoftLink]


def generate_json(
    data: Instrument,
    file,
    nexus_file_name: str = "",
    broker: str = "",
    start_time: str = None,
    stop_time: str = None,
    service_id: str = None,
    abort_uninitialised: bool = False,
    use_swmr: bool = True,
):
    """
    Returns a formatted json string built from a given Instrument
    The json description can be used by the file writer (github.com/ess-dmsc/kafka-to-nexus) to create a NeXus file

    :param data: The full description of the beamline and data
    :param file: the file object to output the JSON to.
    :param streams: dict of streams in nexus file.
    :param links: dict of links in nexus file with name and target as value fields.
    :param nexus_file_name: The NeXus file name in the write command for the filewriter.
    """

    converter = NexusToDictConverter()
    tree = converter.convert(data.nexus.nexus_file)
    write_command, _ = create_writer_commands(
        tree,
        nexus_file_name,
        broker=broker,
        start_time=start_time,
        stop_time=stop_time,
        service_id=service_id,
        abort_on_uninitialised_stream=abort_uninitialised,
        use_hdf_swmr=use_swmr,
    )
    object_to_json_file(write_command, file)


def cast_to_int(data):
    """
    Python 3+ has an unlimited-size integer representation
    We can convert any numpy integer type to Python int for serialising to JSON
    """
    if isinstance(data, list):
        return data
    else:
        return int(data)


ATTR_NAME_BLACKLIST = ["dependee_of"]
NX_CLASS_BLACKLIST = ["NXgroup", "NCstream"]


def _add_attributes(root: NexusObject, root_dict: dict):
    attrs = []
    for attr_name, attr in root.attrs.items():
        if attr_name == "NX_class" and attr in NX_CLASS_BLACKLIST:
            break
        if attr_name not in ATTR_NAME_BLACKLIST:
            if isinstance(attr, bytes):
                attr = attr.decode("utf8")
            new_attribute = {"name": attr_name, "values": attr}
            attrs.append(new_attribute)
    if attrs:
        root_dict["attributes"] = attrs
    return root_dict


def get_data_and_type(root: h5py.Dataset):
    """
    get the value and data type of dataset
    :param root: h5py dataset
    :return: the data in the dataset, the datatype and the size of the data in the dataset
    """
    size = 1
    data = root[()]
    dtype = root.dtype
    if type(data) is np.ndarray:
        size = data.shape
        data = data.tolist()
    if dtype.char == "S" or dtype == h5py.special_dtype(vlen=str):
        try:
            if isinstance(data, list):
                data = [str_item.decode("utf-8") for str_item in data]
            else:
                data = data.decode("utf-8")
        except AttributeError:  # Already a str (decoded)
            pass
        dtype = "string"
    elif dtype == np.float32:
        dtype = "float"
    elif dtype == np.float64:
        dtype = "double"
    elif dtype == np.int32:
        dtype = "int32"
        data = cast_to_int(data)
    elif dtype == np.int64:
        dtype = "int64"
        data = cast_to_int(data)
    elif dtype == np.uint32:
        dtype = "uint32"
        data = cast_to_int(data)
    elif dtype == np.uint64:
        dtype = "uint64"
        data = cast_to_int(data)
    else:
        logging.error(
            f"Unrecognised type {dtype}, don't know what to record as in JSON"
        )
    return data, dtype, size


class NexusToDictConverter:
    """
    Class used to convert NeXus format root to python dict
    """

    def convert(self, nexus_root: NexusObject):
        """
        Converts the given nexus_root to dict with correct replacement of
        the streams
        :param nexus_root: the root object to convert from NeXus to JSON
        :return: dictionary
        """
        return {
            "children": [self._root_to_dict(entry) for _, entry in nexus_root.items()]
        }

    def _root_to_dict(self, root: NexusObject):
        if isinstance(root, h5py.Group):
            root_dict = self._handle_group(root)
        else:
            root_dict = self._handle_dataset(root)

        root_dict = _add_attributes(root, root_dict)
        return root_dict

    def _handle_group(self, root: h5py.Group):
        """
        Generate JSON dict for a h5py group.
        :param root: h5py group to generate dict from.
        :return: generated dict of group and children.
        """
        root_dict = {"type": "group", "name": get_name_of_node(root), "children": []}
        # Add the entries
        if get_nx_class(root) == "NCstream":
            self._handle_stream(root, root_dict)

        for entry in root.values():
            # Check if there are SoftLinks in the group
            if isinstance(root.get(name=entry.name, getlink=True), h5py.SoftLink):
                self._handle_link(entry, root, root_dict)
            root_dict["children"].append(self._root_to_dict(entry))

        return root_dict

    @staticmethod
    def _handle_link(entry: NexusObject, root: h5py.Group, root_dict: Dict):
        """
        Create link specific fields in the JSON when a softlink is found.
        :param entry: The entry (dataset or group) that is to be linked
        :param root: the group containing the link object
        :param root_dict: the output dictionary for the JSON writer
        """
        root_dict["children"].append(
            {
                "type": "link",
                "name": get_name_of_node(entry),
                "target": root.get(name=entry.name, getlink=True).path,
            }
        )

    @staticmethod
    def _handle_stream(root: h5py.Group, root_dict: Dict):
        """
        Given a stream group handle the stream-specific fields in the JSON
        :param root: group containing stream fields
        :param root_dict: JSON output dictionary
        """
        item_dict = dict()
        for name, item in root.items():
            dots_in_field_name = name.split(".")
            if len(dots_in_field_name) > 1:
                _separate_dot_field_group_hierarchy(item_dict, dots_in_field_name, item)
            else:
                item_dict[name] = item[...][()]
        root_dict["children"].append({"type": "stream", "stream": item_dict})

    @staticmethod
    def _handle_dataset(root: Union[h5py.Dataset, h5py.SoftLink]):
        """
        Generate JSON dict for a h5py dataset.
        :param root: h5py dataset to generate dict from.
        :return: generated dictionary of dataset values and attrs.
        """
        data, dataset_type, size = get_data_and_type(root)

        root_dict = {
            "type": "dataset",
            "name": get_name_of_node(root),
            "dataset": {"type": dataset_type},
            "values": data,
        }
        if size != 1:
            root_dict["dataset"]["size"] = size

        return root_dict


def create_writer_commands(
    nexus_structure,
    output_filename,
    broker,
    job_id="",
    start_time=None,
    stop_time=None,
    use_hdf_swmr=True,
    service_id=None,
    abort_on_uninitialised_stream=False,
):
    """
    :param nexus_structure: dictionary containing nexus file structure
    :param output_filename: the nexus file output filename
    :param broker: default broker to consume from
    :param job_id: filewriter job_id
    :param start_time: ms from unix epoch
    :param stop_time: ms from unix epoch
    :param abort_on_uninitialised_stream: Whether to abort if the stream cannot be initialised
    :param service_id: The identifier for the instance of the file-writer that should handle this command. Only needed if multiple file-writers present
    :param use_hdf_swmr: Whether to use HDF5's Single Writer Multiple Reader (SWMR) capabilities. Default is true in the filewriter
    :return: A write command and stop command with specified job_id.
    """
    if not job_id:
        job_id = str(uuid.uuid1())

    write_cmd = {
        "cmd": "FileWriter_new",
        "broker": broker,
        "job_id": job_id,
        "file_attributes": {"file_name": output_filename},
        "nexus_structure": nexus_structure,
    }
    if start_time is not None:
        write_cmd["start_time"] = start_time
    if not use_hdf_swmr:
        write_cmd["use_hdf_swmr"] = use_hdf_swmr

    if abort_on_uninitialised_stream:
        write_cmd["abort_on_uninitialised_stream"] = abort_on_uninitialised_stream

    stop_cmd = {"cmd": "FileWriter_stop", "job_id": job_id}
    if stop_time is not None:
        write_cmd["stop_time"] = stop_time
        stop_cmd["stop_time"] = stop_time

    if service_id is not None and service_id:
        write_cmd["service_id"] = service_id
        stop_cmd["service_id"] = service_id

    return write_cmd, stop_cmd


def _separate_dot_field_group_hierarchy(
    item_dict: Dict[Any, Any],
    dots_in_field_name: List[str],
    item: Tuple[str, h5py.Group],
):
    previous_group = item_dict
    for subgroup in dots_in_field_name:
        # do not overwrite a group unless it doesn't yet exist
        if subgroup not in previous_group:
            previous_group[subgroup] = dict()
        if subgroup == dots_in_field_name[-1]:
            # set the value of the field to the last item in the list
            previous_group[subgroup] = item[...][()]
        previous_group = previous_group[subgroup]
