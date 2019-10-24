import h5py
import numpy as np
import uuid
import logging
from typing import Union

from nexus_constructor.instrument import Instrument
from nexus_constructor.json.helpers import object_to_json_file


NexusObject = Union[h5py.Group, h5py.Dataset]


def generate_json(
    data: Instrument,
    file,
    streams=None,
    links=None,
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

    if links is None:
        links = {}
    if streams is None:
        streams = {}

    converter = NexusToDictConverter()
    tree = converter.convert(data.nexus.nexus_file, streams, links)
    write_command, stop_command = create_writer_commands(
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
        return [int(data_value) for data_value in data]
    else:
        return int(data)


def _add_attributes(root: NexusObject, root_dict: dict):
    if "attributes" not in root_dict:
        root_dict["attributes"] = []
    root_dict["attributes"] = []
    for attr_name, attr in root.attrs.items():
        if isinstance(attr, bytes):
            attr = attr.decode("utf8")
        new_attribute = {"name": attr_name, "values": attr}
        root_dict["attributes"].append(new_attribute)


class NexusToDictConverter:
    """
    Class used to convert nexus format root to python dict
    """

    def __init__(self):
        self._kafka_streams = dict()
        self._links = dict()

    def convert(self, nexus_root: NexusObject, streams: dict, links: dict):
        """
        Converts the given nexus_root to dict with correct replacement of
        the streams
        :param links:
        :param nexus_root
        :param streams:
        :return: dictionary
        """
        self._kafka_streams = streams
        self._links = links
        return {
            "children": [self._root_to_dict(entry) for _, entry in nexus_root.items()]
        }

    def _root_to_dict(self, root: NexusObject):
        if isinstance(root, h5py.Group):
            root_dict = self._handle_group(root)
        else:
            root_dict = self._handle_dataset(root)

        root_dict = self._handle_attributes(root, root_dict)
        return root_dict

    @staticmethod
    def _get_data_and_type(root: h5py.Dataset):
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

    @staticmethod
    def _handle_attributes(root: NexusObject, root_dict: dict):
        if "NX_class" in root.attrs:
            nx_class = root.attrs["NX_class"]
            if (
                nx_class
                and nx_class != "NXfield"
                and nx_class != "NXgroup"
                and nx_class != "NCstream"
            ):
                if isinstance(nx_class, bytes):
                    nx_class = nx_class.decode("utf8")
                root_dict["attributes"] = [{"name": "NX_class", "values": nx_class}]
            if len(root.attrs) > 1:
                _add_attributes(root, root_dict)
        else:
            _add_attributes(root, root_dict)
        return root_dict

    def _handle_group(self, root: h5py.Group):
        """
        Generate JSON dict for a h5py group.
        :param root: h5py group to generate dict from.
        :return: generated dict of group and children.
        """
        root_dict = {"type": "group", "name": root.name, "children": []}
        # Add the entries
        entries = list(root.values())
        if root.name in self._kafka_streams:
            root_dict = {"type": "stream", "stream": self._kafka_streams[root.name]}

        elif root.name in self._links.keys():
            root_dict = {
                "type": "link",
                "name": root.name.split("/")[-1],
                "target": self._links[root.name].file.get(root.name, getlink=True).path,
            }
        elif entries:
            for entry in entries:
                child_dict = self._root_to_dict(entry)
                root_dict["children"].append(child_dict)

        return root_dict

    def _handle_dataset(self, root: h5py.Dataset):
        """
        Generate JSON dict for a h5py dataset.
        :param root: h5py dataset to generate dict from.
        :return: generated dictionary of dataset values and attrs.
        """
        data, dataset_type, size = self._get_data_and_type(root)
        root_dict = {
            "type": "dataset",
            "name": root.name,
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
