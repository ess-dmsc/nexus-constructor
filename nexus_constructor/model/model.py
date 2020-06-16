import json

from PySide2.QtCore import QObject, Signal
from typing import Dict, Any

from nexus_constructor.model.entry import Entry
from nexus_constructor.model.instrument import Instrument


class Signals(QObject):
    """
    Signals when model is updated, to trigger, for example, updating the 3D view
    """

    file_changed = Signal("QVariant")
    file_opened = Signal("QVariant")
    component_added = Signal(str, "QVariant", "QVariant")
    component_removed = Signal(str)
    transformation_changed = Signal()
    show_entries_dialog = Signal("QVariant", "QVariant")


class Model:
    def __init__(self, entry: Entry):
        self.signals = Signals()
        self.entry = entry
        self.temp_entry = None

    def as_dict(self) -> Dict[str, Any]:
        return {"nexus_structure": {"children": [self.entry.as_dict()]}}

    def load_json_file(self, json_data: str):

        self.temp_entry = Entry()
        self.entry.instrument = Instrument()

        entry = json.loads(json_data, object_hook=self.parse_json)

        if entry is not None:
            self.entry = self.temp_entry
            self.temp_entry = None
            return True
        else:
            return False

    def parse_json(self, json_entry: dict):

        name = json_entry.get("name")

        if name == "nexus_structure":
            self.parse_json(json_entry.get("children"))
        elif name == "entry":
            print(json_entry)
        elif name == "instrument":
            print(json_entry)
        elif name == "transformations":
            for child in json_entry.get("children"):
                self.parse_json(child)
