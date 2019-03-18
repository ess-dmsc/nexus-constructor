from uuid import uuid4

import h5py
from PySide2.QtCore import Qt, QObject, Signal, Property


def create_group(name, nx_class, parent):
    group = parent.create_group(name)
    group.attrs["NX_class"] = nx_class
    return group


class NexusModel(QObject):
    """
    Stores InstrumentModel data in nexus compliant hdf5 files
    """

    def __init__(self):
        super().__init__()
        file_name = str(uuid4())
        self.instrument = False

        self.nexus_file = h5py.File(file_name, driver="core", backing_store=False)

        self.entry = create_group("entry", "NXentry", self.nexus_file)

        self.setInstrumentGroup(create_group("instrument", "NXinstrument", self.entry))

    @Signal
    def group_changed(self):
        pass

    def getInstrumentGroup(self):
        return self.instrument

    def setInstrumentGroup(self, group):
        self.instrument = group

    instrumentGroup = Property(
        "QVariant", getInstrumentGroup, setInstrumentGroup, notify=group_changed
    )
