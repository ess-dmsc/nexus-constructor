import h5py

from PySide2.QtCore import Signal, QObject
from typing import Any
import numpy as np


def set_up_in_memory_nexus_file(filename):
    """
    Creates an in-memory nexus-file to store the model data in.
    :return: The file object.
    """
    return h5py.File(filename, mode="x", driver="core", backing_store=False)


def append_nxs_extension(file_name):
    extension = ".nxs"
    if file_name.endswith(extension):
        return file_name
    else:
        return file_name + extension


def get_name_of_group(group: h5py.Group):
    return group.name.split("/")[-1]


class NexusWrapper(QObject):
    """
    Contains the NeXus file and functions to add and edit components in the NeXus file structure.
    All changes to the NeXus file should happen via this class. Emits Qt signal whenever anything in the file changes.
    """

    # Signal that indicates the nexus file has been changed in some way
    file_changed = Signal("QVariant")
    component_added = Signal(str, "QVariant")

    def __init__(self, filename="NeXus File"):
        super().__init__()
        self.nexus_file = set_up_in_memory_nexus_file(filename)
        self.entry = self.create_nx_group("entry", "NXentry", self.nexus_file)

        self.create_nx_group("sample", "NXsample", self.entry)
        self.instrument = self.create_nx_group("instrument", "NXinstrument", self.entry)

        self._emit_file()

    def _emit_file(self):
        """
        Calls the file_changed signal with the updated file object when the structure is changed.
        :return: None
        """
        self.file_changed.emit(self.nexus_file)

    def save_file(self, filename):
        """
        Saves the in-memory NeXus file to a physical file if the filename is valid.
        :param filename: Absolute file path to the file to save.
        :return: None
        """
        if filename:
            print(filename)
            file = h5py.File(append_nxs_extension(filename), mode="x")
            try:
                file.copy(source=self.nexus_file["/entry/"], dest="/entry/")
                print("Saved to NeXus file")
            except ValueError as e:
                print(f"File writing failed: {e}")

    def open_file(self, filename):
        """
        Opens a physical file into memory and sets the model to use it.
        :param filename: Absolute file path to the file to open.
        :return:
        """
        if filename:
            print(filename)
            self.nexus_file = h5py.File(
                filename, mode="r", backing_store=False, driver="core"
            )
            print("NeXus file loaded")
            self._emit_file()

    def rename_group(self, group: h5py.Group, new_name: str):
        self.nexus_file.move(group.name, f"{self.group.parent.name}/{new_name}")

    def create_nx_group(self, name, nx_class, parent):
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

    @staticmethod
    def get_nx_class(group: h5py.Group):
        if "NX_class" in group.attrs.keys():
            return None
        return group.attrs["NX_class"][:].decode()

    def set_nx_class(self, group: h5py.Group, nx_class: str):
        group.attrs["NX_class"] = nx_class
        self._emit_file()

    @staticmethod
    def get_field_value(group: h5py.Group, name: str):
        if name not in group:
            raise NameError(f"Field called {name} not found in {group.name}")
        return group[name][...]

    def set_field_value(self, group: h5py.Group, name: str, value: Any, dtype=None):
        if dtype is str:
            dtype = f'|S{len(value)}'
            value = np.array(value).astype(dtype)

        if name in group:
            if dtype is None or group[name].dtype == dtype:
                group[name][...] = value
            else:
                del group[name]
                group.create_dataset(name, data=value, dtype=dtype)
        else:
            group.create_dataset(name, data=value, dtype=dtype)
        self._emit_file()

    def add_transformation(self):
        raise NotImplementedError

    def remove_transformation(self):
        raise NotImplementedError
