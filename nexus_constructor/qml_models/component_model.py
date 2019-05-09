from uuid import uuid4

import h5py
from PySide2.QtCore import QObject, Signal, Slot, Property
from nexus_constructor.nexus_model import (
    create_group,
    get_nx_class_for_component,
    get_informal_name_for_nxcomponent,
)


class ComponentModel(QObject):
    def __init__(self):
        super().__init__()
        file_name = str(uuid4())

        temp_file = h5py.File(file_name, mode="w", driver="core", backing_store=False)
        self.group = temp_file.create_group("component")
        self.description_dataset = self.group.create_dataset(
            "/description", (100,), h5py.special_dtype(vlen=str)
        )
        self.description_dataset.data = ""
        self.something = True
        self.somethingelse = False

    @Slot("QVariant")
    def copy_component_to_instrument(self, instrument_group):
        self.group.copy(instrument_group)

    component_changed = Signal()

    def get_group_name(self):
        return self.group.name

    def set_group_name(self, name):
        self.group.name = name

    def get_component_type(self):
        return get_informal_name_for_nxcomponent(self.group.attr["NX_class"])

    def set_component_type(self, component_type):
        self.group.attr["NX_class"] = get_nx_class_for_component(component_type)

    def get_description(self):
        return self.description_dataset.data

    def set_description(self, desc):
        self.description_dataset.data = desc

    component_group_name = Property(
        str, get_group_name, set_group_name, notify=component_changed
    )
    component_type = Property(
        str, get_component_type, set_component_type, notify=component_changed
    )

    description = Property(
        str, get_description, set_description, notify=component_changed
    )
