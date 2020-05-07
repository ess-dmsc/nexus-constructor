from PySide2.QtCore import QObject, Signal

from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group


def _convert_name_with_spaces(component_name: str) -> str:
    return component_name.replace(" ", "_")


class Nexus(QObject):
    """
    Used for storing the signals for updating the "file" - currently just needed to avoid changing the interface of Instrument
    """

    file_changed = Signal("QVariant")
    file_opened = Signal("QVariant")
    component_added = Signal(str, "QVariant", "QVariant")
    component_removed = Signal(str)
    transformation_changed = Signal()
    show_entries_dialog = Signal("QVariant", "QVariant")


class Instrument(Group):
    def __init__(self):
        super().__init__("instrument")
        self.nx_class = "NXinstrument"
        self.nexus = Nexus()

    def get_component_list(self):
        sample = Component("sample")
        sample.nx_class = "NXsample"
        return [sample]


class Entry(Group):
    def __init__(self):
        super().__init__("entry")
        self.nx_class = "NXentry"

    @property
    def instrument(self) -> Instrument:
        return self["instrument"]

    @instrument.setter
    def instrument(self, instrument: Instrument):
        self["instrument"] = instrument
