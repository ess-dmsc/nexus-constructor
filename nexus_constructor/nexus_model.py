from uuid import uuid4
import h5py
from PySide2.QtCore import QObject, Property, Slot, QUrl
from nexus_constructor.component_type import ComponentType


def create_group(name, nx_class, parent):
    """
    Given a name, an nx class and a parent group, create a group under the parent
    :param name: The name of the group to be created.
    :param nx_class: The NX_class attribute to be set.
    :param parent: The parent HDF group to add the created group to.
    :return: A reference to the created group in the in-memory NeXus file.
    """
    group = parent.create_group(name)
    group.attrs["NX_class"] = nx_class
    return group


def get_nx_class_for_component(component_type):
    """
    Returns the NX class for a given component.
    :param component_type: the component type of the object being added
    :return: String containing the name of the NX class eg NXdetector
    """
    return f"NX{ComponentType(component_type).name.lower()}".replace(" ", "_")


def get_informal_name_for_nxcomponent(component_name: str):
    return component_name.lstrip("NX").replace("_", " ")


def append_nxs_extension(file_name):
    extension = ".nxs"
    if file_name.endswith(extension):
        return file_name
    else:
        return file_name + extension


class NexusModel(QObject):
    """
    Stores InstrumentModel data in NeXus compliant hdf5 files
    The entry property is read-only.
    """

    def getEntryGroup(self):
        return self.entry

    entryGroup = Property("QVariant", getEntryGroup, notify=lambda: None)

    def __init__(self):
        super().__init__()
        file_name = str(uuid4())

        self.nexus_file = h5py.File(
            file_name, mode="w", driver="core", backing_store=False
        )

        self.entry = create_group("entry", "NXentry", self.nexus_file)

    @Slot("QVariant")
    def write_to_file(self, file_name):
        output = h5py.File(
            append_nxs_extension(
                file_name.toString(options=QUrl.FormattingOptions(QUrl.PreferLocalFile))
            ),
            mode="w",
        )
        output.copy(source=self.getEntryGroup(), dest="/entry/")
