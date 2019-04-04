from uuid import uuid4
import h5py
from PySide2.QtCore import QObject, Signal, Property
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
    nxclass = f"NX{ComponentType(component_type).name.lower()}".replace(" ", "_")
    return nxclass


class NexusModel(QObject):
    """
    Stores InstrumentModel data in NeXus compliant hdf5 files
    """

    def __init__(self):
        super().__init__()
        file_name = str(uuid4())
        self.instrument = False

        self.nexus_file = h5py.File(
            file_name, mode="w", driver="core", backing_store=False
        )

        self.entry = create_group("entry", "NXentry", self.nexus_file)

        self.instrument = create_group("instrument", "NXinstrument", self.entry)

    @Signal
    def entry_group_changed(self):
        pass

    def getEntryGroup(self):
        return self.entry

    def setEntryGroup(self, group):
        """
        The variable itself should be read-only, so this function does nothing.
        """
        pass

    entryGroup = Property(
        "QVariant", getEntryGroup, setEntryGroup, notify=entry_group_changed
    )

    @Signal
    def instrument_group_changed(self):
        pass

    def getInstrumentGroup(self):
        return self.instrument

    def setInstrumentGroup(self, group):
        """
        The variable itself should be read-only, so this function does nothing.
        """
        pass

    instrumentGroup = Property(
        "QVariant",
        getInstrumentGroup,
        setInstrumentGroup,
        notify=instrument_group_changed,
    )
