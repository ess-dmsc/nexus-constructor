from nexus_constructor.model.group import Group
from nexus_constructor.model.instrument import Instrument
from typing import Dict, Any


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

    def as_dict(self) -> Dict[str, Any]:
        dictionary = super(Entry, self).as_dict()
        # sample lives in instrument component list for purposes of GUI
        # but in the NeXus structure must live in the entry
        try:
            dictionary["children"].append(self.instrument.sample.as_dict())
        except AttributeError:
            # If instrument is not set then don't try to add sample to dictionary
            pass
        return dictionary
