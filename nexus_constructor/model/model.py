import json

from PySide2.QtCore import QObject, Signal
from typing import Dict, Any

from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.instrument import Instrument

ignore = ["entry", "instrument", "transformations", "NX_class"]


def _parse_nx_class(entry: list):

    for item in entry:
        if item.get("NX_class"):
            return item.get("values")

    return None


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
        self.temp_entry.instrument = Instrument()

        json_dict = json.loads(json_data)

        try:
            children_list = json_dict["nexus_structure"]["children"][0]["children"]
        except KeyError:
            return False

        if all(self.parse_json(child) for child in children_list):
            self.entry = self.temp_entry
            self.temp_entry = None
            return True
        else:
            return False

    def parse_json(self, json_entry: dict):

        name = json_entry.get("name")

        if name == "instrument":
            return True

        elif name and name not in ignore:

            nx_class = _parse_nx_class(json_entry.get("attributes"))

            if nx_class is None:
                return False

            elif nx_class == "NX_sample":
                component = self.temp_entry.instrument.sample
                component.name = name
            else:
                component = Component(name)
                self.temp_entry.instrument.add_component(component)

            # todo: recover transformations

            return True

        return False
