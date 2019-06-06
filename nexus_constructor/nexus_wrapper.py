import h5py

from nexus_constructor.qml_models import instrument_model
from PySide2.QtCore import Signal, QObject

COMPS_IN_ENTRY = ["NXdetector", "NXsample"]


def set_up_in_memory_nexus_file():
    return h5py.File("nexus-constructor", mode="x", driver="core", backing_store=False)


class NexusWrapper(QObject):
    file_changed = Signal("QVariant")

    def __init__(self):
        super().__init__()
        self.nexus_file = set_up_in_memory_nexus_file()
        self.entry_group = self.nexus_file.create_group("entry")
        self.entry_group.attrs["NX_class"] = "NXentry"
        self.instrument_group = self.entry_group.create_group("instrument")
        self.instrument_group.attrs["NX_class"] = "NXinstrument"

        self.components_list_model = instrument_model.InstrumentModel()
        self.components_list_model.initialise(self.entry_group)
        self._emit_file()

    def _emit_file(self):
        self.file_changed.emit(self.nexus_file)

    def get_component_list(self):
        return self.components_list_model

    def save_file(self, filename):
        if filename:
            print(filename)
            file = h5py.File(filename, mode="x")
            try:
                file.copy(source=self.nexus_file["/entry/"], dest="/entry/")
                print("Saved to NeXus file")
            except ValueError as e:
                print(f"File writing failed: {e}")

    def open_file(self, filename):
        if filename:
            print(filename)
            self.nexus_file = h5py.File(
                filename, mode="r", backing_store=False, driver="core"
            )
            print("NeXus file loaded")
            self._emit_file()

    def add_component(self, component_type, component_name, description, geometry):
        self.components_list_model.add_component(
            component_type=component_type,
            description=description,
            name=component_name,
            geometry_model=geometry,
        )

        instrument_group = self.entry_group["instrument"]

        if component_type in COMPS_IN_ENTRY:
            # If the component should be put in entry rather than instrument
            instrument_group = self.entry_group

        component_group = instrument_group.create_group(component_name)
        component_group.attrs["NX_class"] = component_type

        self._emit_file()
