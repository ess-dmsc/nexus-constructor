import logging
import uuid

import h5py
from PySide2.QtCore import Signal, QObject
from typing import Any, TypeVar, Optional, List
import numpy as np

from nexus_constructor.invalid_field_names import INVALID_FIELD_NAMES


h5Node = TypeVar("h5Node", h5py.Group, h5py.Dataset)


def set_up_in_memory_nexus_file(filename: str) -> h5py.File:
    """
    Creates an in-memory nexus-file to store the model data in.
    :return: The file object.
    """
    return h5py.File(filename, mode="x", driver="core", backing_store=False)


def append_nxs_extension(file_name: str) -> str:
    extension = ".nxs"
    if file_name.endswith(extension):
        return file_name
    else:
        return file_name + extension


def get_name_of_node(node: h5Node) -> str:
    return node.name.split("/")[-1]


def get_nx_class(group: h5py.Group) -> Optional[str]:
    if "NX_class" not in group.attrs.keys():
        return None

    nx_class = group.attrs["NX_class"]
    return decode_bytes_string(nx_class)


def decode_bytes_string(nexus_string):
    try:
        return str(nexus_string, encoding="utf8")
    except TypeError:
        return nexus_string


def create_temporary_in_memory_file() -> h5py.File:
    """
    Create a temporary in-memory nexus file with a random name.
    :return: The file object
    """
    return set_up_in_memory_nexus_file(str(uuid.uuid4()))


def get_fields(
    group: h5py.Group
) -> (List[h5py.Dataset], List[h5py.Dataset], List[h5py.Group], List[h5py.Group]):
    """
    Return a list of fields in a given component group.
    :param group: The hdf5 component group to check for fields
    :return: A list of a fields, regardless of field type
    """
    scalar_fields = []
    array_fields = []
    stream_fields = []
    link_fields = []
    for item in group.values():
        if (
            isinstance(item, h5py.Dataset)
            and item.name.split("/")[-1] not in INVALID_FIELD_NAMES
        ):
            if np.isscalar(item[()]):
                scalar_fields.append(item)
                continue
            array_fields.append(item)
        elif isinstance(item, h5py.Group):
            if isinstance(item.parent.get(item.name, getlink=True), h5py.SoftLink):
                link_fields.append(item)
            elif (
                "NX_class" in item.attrs.keys() and item.attrs["NX_class"] == "NCstream"
            ):
                stream_fields.append(item)
    return scalar_fields, array_fields, stream_fields, link_fields


class NexusWrapper(QObject):
    """
    Contains the NeXus file and functions to add and edit components in the NeXus file structure.
    All changes to the NeXus file should happen via this class. Emits Qt signal whenever anything in the file changes.
    """

    # Signal that indicates the nexus file has been changed in some way
    file_changed = Signal("QVariant")
    file_opened = Signal("QVariant")
    component_added = Signal(str, "QVariant", "QVariant")
    component_removed = Signal(str)
    transformation_changed = Signal()
    show_entries_dialog = Signal("QVariant", "QVariant")

    def __init__(
        self,
        filename: str = "NeXus File",
        entry_name: str = "entry",
        instrument_name: str = "instrument",
    ):
        super().__init__()
        self.nexus_file = set_up_in_memory_nexus_file(filename)
        self.entry = self.create_nx_group(entry_name, "NXentry", self.nexus_file)
        self.instrument = self.create_nx_group(
            instrument_name, "NXinstrument", self.entry
        )
        self.create_nx_group("sample", "NXsample", self.entry)

        self._emit_file()

    def _emit_file(self):
        """
        Calls the file_changed signal with the updated file object when the structure is changed.
        :return: None
        """
        self.file_changed.emit(self.nexus_file)

    def save_file(self, filename: str):
        """
        Saves the in-memory NeXus file to a physical file if the filename is valid.
        :param filename: Absolute file path to the file to save.
        :return: None
        """
        if filename:
            logging.debug(filename)
            file = h5py.File(append_nxs_extension(filename), mode="x")
            try:
                file.copy(
                    source=self.nexus_file["/entry/"],
                    dest="/entry/",
                    without_attrs=False,
                )
                logging.info("Saved to NeXus file")
            except ValueError as e:
                logging.error(f"File writing failed: {e}")

    def open_file(self, filename: str):
        """
        Opens a physical file into memory and sets the model to use it.
        :param filename: Absolute file path to the file to open.
        :return:
        """
        if filename:
            nexus_file = h5py.File(
                filename, mode="r+", backing_store=False, driver="core"
            )
            return self.load_nexus_file(nexus_file)

    def load_nexus_file(self, nexus_file: h5py.File):
        entries = self.find_entries_in_file(nexus_file)
        self.file_opened.emit(nexus_file)
        return entries

    def find_entries_in_file(self, nexus_file: h5py.File):
        """
        Find the entry group in the specified nexus file. If there are multiple, emit the signal required to
        show the multiple entry selection dialog in the UI.
        :param nexus_file: A reference to the nexus file to check for the entry group.
        """
        entries_in_root = dict()

        def append_nx_entries_to_list(name, node):
            if isinstance(node, h5py.Group):
                if "NX_class" in node.attrs.keys():
                    if (
                        node.attrs["NX_class"] == b"NXentry"
                        or node.attrs["NX_class"] == "NXentry"
                    ):
                        entries_in_root[name] = node

        nexus_file["/"].visititems(append_nx_entries_to_list)
        if len(entries_in_root.keys()) > 1:
            self.show_entries_dialog.emit(entries_in_root, nexus_file)
            return False
        else:
            self.load_file(list(entries_in_root.values())[0], nexus_file)
            return True

    def load_file(self, entry: h5py.Group, nexus_file: h5py.File):
        """
        Sets the entry group, instrument group and reference to the nexus file.
        :param entry: The entry group.
        :param nexus_file: The nexus file reference.
        """
        self.entry = entry
        self.instrument = self.get_instrument_group_from_entry(self.entry)
        self.nexus_file = nexus_file
        self._generate_dependee_of_attributes()
        logging.info("NeXus file loaded")
        self._emit_file()

    def rename_node(self, node: h5Node, new_name: str):
        self.nexus_file.move(node.name, f"{node.parent.name}/{new_name}")
        self._emit_file()

    def delete_node(self, node: h5Node):
        del self.nexus_file[node.name]
        self._emit_file()

    def create_nx_group(
        self, name: str, nx_class: str, parent: h5py.Group
    ) -> h5py.Group:
        """
        Given a name, an nx class and a parent group, create a group under the parent
        :param name: The name of the group to be created.
        :param nx_class: The NX_class attribute to be set.
        :param parent: The parent HDF group to add the created group to.
        :return: A reference to the created group in the in-memory NeXus file.
        """
        group = parent.create_group(name)
        group.attrs["NX_class"] = nx_class
        self._emit_file()
        return group

    def _generate_dependee_of_attributes(self):
        """
        Fill in the dependee_of attribute for transformations that are linked to.
        """
        component_depends_on = {}

        def find_depends_on_for_components(_, node):
            if isinstance(node, h5py.Group):
                if "depends_on" in node.keys():
                    component_depends_on[node.name] = node["depends_on"][()]

        self.nexus_file["/"].visititems(find_depends_on_for_components)

        transforms_dependee_of = {}
        for group_name, depends_on_transform in component_depends_on.items():
            if depends_on_transform not in transforms_dependee_of.keys():
                transforms_dependee_of[depends_on_transform] = []
            transforms_dependee_of[depends_on_transform].append(group_name)

        for transform, dependee_of in transforms_dependee_of.items():
            # numpy should cast to a scalar value if there is just one item.
            self.nexus_file[transform].attrs["dependee_of"] = np.array(
                dependee_of, dtype=h5py.special_dtype(vlen=str)
            )

    def duplicate_nx_group(
        self, group_to_duplicate: h5py.Group, new_group_name: str
    ) -> h5py.Group:

        group_to_duplicate.copy(
            dest=group_to_duplicate.parent,
            source=group_to_duplicate,
            name=new_group_name,
        )
        self._emit_file()
        return group_to_duplicate.parent[new_group_name]

    def set_nx_class(self, group: h5py.Group, nx_class: str):
        group.attrs["NX_class"] = nx_class
        self._emit_file()

    @staticmethod
    def get_field_value(group: h5py.Group, name: str) -> Optional[Any]:
        if name not in group:
            return None
        value = group[name][...]
        if value.dtype.type is np.string_:
            value = str(value, "utf8")
        elif (
            group[name].dtype.metadata is not None
            and "vlen" in group[name].dtype.metadata.keys()
            and group[name].dtype.metadata["vlen"] == str
        ):
            value = str(value.astype(np.string_), "utf8")
        return value

    @staticmethod
    def _recreate_dataset(parent_group: h5py.Group, name: str, value: Any, dtype=None):
        del parent_group[name]
        return parent_group.create_dataset(name, data=value, dtype=dtype)

    def set_field_value(
        self, group: h5py.Group, name: str, value: Any, dtype=None
    ) -> h5py.Dataset:
        """
        Create or update the value of a field (dataset in hdf terminology)
        :param group: Parent group of the field.
        :param name: Name of the field.
        :param value: Value of the field.
        :param dtype: Type of the value (Use numpy types)
        :return: The dataset.
        """

        if isinstance(value, h5py.SoftLink):
            group[name] = value
            return group[name]

        if isinstance(value, h5py.Group):
            if name in group:
                del group[name]
            value.copy(dest=group, source=value)
            return group[name]

        if dtype is str:
            dtype = f"|S{len(value)}"
            value = np.array(value).astype(dtype)

        if dtype == np.object:
            dtype = h5py.special_dtype(vlen=str)
        ds = None
        if name in group:
            if dtype is None or group[name].dtype == dtype:
                try:
                    group[name][...] = value
                except TypeError:
                    ds = self._recreate_dataset(group, name, value, dtype)
            else:
                ds = self._recreate_dataset(group, name, value, dtype)
        else:
            ds = group.create_dataset(name, data=value, dtype=dtype)

        try:
            for k, v in value.attrs.items():
                ds.attrs[k] = v
        except AttributeError:
            pass

        self._emit_file()
        return group[name]

    def delete_field_value(self, group: h5py.Group, name: str):
        try:
            del group[name]
            self._emit_file()
        except KeyError:
            pass

    @staticmethod
    def get_attribute_value(node: h5Node, name: str) -> Optional[Any]:
        if name in node.attrs.keys():
            value = node.attrs[name]
            if isinstance(value, bytes):
                return value.decode("utf-8")
            return value

    def set_attribute_value(self, node: h5Node, name: str, value: Any):
        # Deal with arrays of strings
        if isinstance(value, np.ndarray):
            if value.dtype.type is np.str_ and value.size == 1:
                value = str(value[0])
            elif value.dtype.type is np.str_ and value.size > 1:
                node.attrs.create(
                    name, value, (len(value),), h5py.special_dtype(vlen=str)
                )
                for index, item in enumerate(value):
                    node.attrs[name][index] = item.encode("utf-8")
                self._emit_file()
                return

        node.attrs[name] = value
        self._emit_file()

    def delete_attribute(self, node: h5Node, name: str):
        if name in node.attrs.keys():
            del node.attrs[name]
        self._emit_file()

    def create_transformations_group_if_does_not_exist(self, parent_group: h5Node):
        for child in parent_group:
            if "NX_class" in parent_group[child].attrs.keys():
                if parent_group[child].attrs["NX_class"] == "NXtransformations":
                    return parent_group[child]
        return self.create_nx_group(
            "transformations", "NXtransformations", parent_group
        )

    @staticmethod
    def get_instrument_group_from_entry(entry: h5py.Group) -> h5py.Group:
        """
        Get the first NXinstrument object from an entry group.
        :param entry: The entry group object to search for the instrument group in.
        :return: the instrument group object.
        """
        for node in entry.values():
            if isinstance(node, h5py.Group):
                if "NX_class" in node.attrs.keys():
                    if node.attrs["NX_class"] in ["NXinstrument", b"NXinstrument"]:
                        return node
