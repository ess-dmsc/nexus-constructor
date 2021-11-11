from typing import Any, Dict, List

from nexus_constructor.common_attrs import INSTRUMENT_NAME, CommonKeys
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.group import Group
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.model.value_type import ValueTypes


NICOS_PLACEHOLDERS = {
    "experiment_identifier": Dataset(
        "experiment_identifier", values="$EXP_ID$", type=ValueTypes.STRING
    )
}


class Entry(Group):
    def __init__(self):
        super().__init__(name="entry", parent_node=None)
        self.nx_class = "NXentry"

    @property
    def instrument(self) -> Instrument:
        return self[INSTRUMENT_NAME]

    @instrument.setter
    def instrument(self, instrument: Instrument):
        self[INSTRUMENT_NAME] = instrument
        instrument.parent_node = self

    def as_dict(self, error_collector: List[str]) -> Dict[str, Any]:
        dictionary = super(Entry, self).as_dict(error_collector)
        # sample lives in instrument component list for purposes of GUI
        # but in the NeXus structure must live in the entry
        try:
            dictionary[CommonKeys.CHILDREN].append(
                self.instrument.sample.as_dict(error_collector)
            )
        except AttributeError:
            # If instrument is not set then don't try to add sample to dictionary
            pass
        self._insert_nicos_placeholders(dictionary, error_collector)
        return dictionary

    def _insert_nicos_placeholders(
        self, dictionary: Dict[str, Any], error_collector: List[str]
    ):
        children = [ds.name for ds in self.children if isinstance(ds, Dataset)]

        for name, place_holder in NICOS_PLACEHOLDERS.items():
            if name not in children:
                dictionary[CommonKeys.CHILDREN].append(
                    place_holder.as_dict(error_collector)
                )
