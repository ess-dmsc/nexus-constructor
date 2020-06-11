from nexus_constructor.model.group import Group
from nexus_constructor.model.instrument import Instrument


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
