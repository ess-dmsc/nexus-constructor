import h5py

from nexus_constructor.qml_models import instrument_model
from PySide2.QtCore import Signal, QObject

COMPS_IN_ENTRY = ["NXmonitor", "NXsample"]


def set_up_in_memory_nexus_file(filename):
    """
    Creates an in-memory nexus-file to store the model data in.
    :return: The file object.
    """
    return h5py.File(filename, mode="x", driver="core", backing_store=False)


class NexusWrapper(QObject):
    """
    Contains the NeXus file and functions to add and edit components in the NeXus file structure.
    Also contains a list of components for use in a listview.
    """

    # Signal that indicates the nexus file has been changed in some way
    file_changed = Signal("QVariant")

    def __init__(self, filename="nexus-constructor"):
        super().__init__()
        self.nexus_file = set_up_in_memory_nexus_file(filename)
        self.entry_group = self.nexus_file.create_group("entry")
        self.entry_group.attrs["NX_class"] = "NXentry"

        sample = self.entry_group.create_group("sample")
        sample.attrs["NX_class"] = "NXsample"

        self.instrument_group = self.entry_group.create_group("instrument")
        self.instrument_group.attrs["NX_class"] = "NXinstrument"

        self.components_list_model = instrument_model.InstrumentModel()
        self._emit_file()

    def _emit_file(self):
        """
        Calls the file_changed signal with the updated file object when the structure is changed.
        :return: None
        """
        self.file_changed.emit(self.nexus_file)

    def get_component_list(self):
        """
        Returns the component list for use with a listview.
        :return: List of components in QAbstractListModel form.
        """
        return self.components_list_model

    def save_file(self, filename):
        """
        Saves the in-memory NeXus file to a physical file if the filename is valid.
        :param filename: Absolute file path to the file to save.
        :return: None
        """
        if filename:
            print(filename)
            file = h5py.File(filename, mode="x")
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

    def add_component(self, component_type, component_name, description, geometry):
        """
        Adds a component to the NeXus file and the components list.
        :param component_type: The NX Component type in string form.
        :param component_name: The Component name.
        :param description: The Component Description.
        :param geometry: Geometry model for the component.
        :return: None
        """
        component_name = convert_name_with_spaces(component_name)
        self.components_list_model.add_component(
            nx_class=component_type,
            description=description,
            name=component_name,
            geometry_model=geometry,
        )

        instrument_group = self.entry_group["instrument"]

        if component_type in COMPS_IN_ENTRY:
            # If the component should be put in /entry/ rather than /instrument/
            instrument_group = self.entry_group

        component_group = instrument_group.create_group(component_name)
        component_group.attrs["NX_class"] = component_type

        self._emit_file()


def convert_name_with_spaces(component_name):
    return component_name.replace(" ", "_")
