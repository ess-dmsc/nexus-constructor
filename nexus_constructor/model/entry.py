from copy import copy
from typing import Any, Dict, List, Tuple

from nexus_constructor.common_attrs import INSTRUMENT_NAME, CommonKeys
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.group import Group
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.model.user import User
from nexus_constructor.model.value_type import ValueTypes


NEXUS_TITLE_NAME = "title"
TITLE_PLACEHOLDER_VALUE = "$TITLE$"
TITLE_PLACEHOLDER = Dataset(
    NEXUS_TITLE_NAME, values=TITLE_PLACEHOLDER_VALUE, type=ValueTypes.STRING
)

NEXUS_EXP_ID_NAME = "experiment_identifier"
EXP_ID_PLACEHOLDER_VALUE = "$EXP_ID$"
EXP_ID_PLACEHOLDER = Dataset(
    NEXUS_EXP_ID_NAME, values=EXP_ID_PLACEHOLDER_VALUE, type=ValueTypes.STRING
)


class Entry(Group):
    def __init__(self):
        super().__init__(name="entry", parent_node=None)
        self.nx_class = "NXentry"
        self._users = []

    @property
    def instrument(self) -> Instrument:
        return self[INSTRUMENT_NAME]

    @instrument.setter
    def instrument(self, instrument: Instrument):
        self[INSTRUMENT_NAME] = instrument
        instrument.parent_node = self

    @property
    def proposal_id(self) -> Tuple[str, bool]:
        return self._read_dataset_property(NEXUS_EXP_ID_NAME, EXP_ID_PLACEHOLDER_VALUE)

    @proposal_id.setter
    def proposal_id(self, values: Tuple[str, bool]):
        self._set_dataset_property(NEXUS_EXP_ID_NAME, EXP_ID_PLACEHOLDER, values)

    @property
    def title(self) -> Tuple[str, bool]:
        return self._read_dataset_property(NEXUS_TITLE_NAME, TITLE_PLACEHOLDER_VALUE)

    @title.setter
    def title(self, values: Tuple[str, bool]):
        self._set_dataset_property(NEXUS_TITLE_NAME, TITLE_PLACEHOLDER, values)

    def _read_dataset_property(self, name: str, value: str) -> Tuple[str, bool]:
        dataset = self[name]
        if dataset:
            return (
                dataset.values,
                True if dataset.values == value else False,
            )
        return "", False

    def users_for_display(self) -> List[Dict[str, str]]:
        return [user.values_dict() for user in self._users]

    def set_users(self, users: List[Dict[str, str]]):
        self._users = []
        for user in users:
            self._users.append(User(None, **user))

    def _set_dataset_property(
        self, name: str, placeholder: Dataset, values: Tuple[str, bool]
    ):
        value, use_default = values
        if not use_default and value.strip() == "":
            del self[name]
            return

        self[name] = copy(placeholder)  # type: ignore

        if not use_default:
            self[name].values = value.strip()

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

        for user in self._users:
            dictionary[CommonKeys.CHILDREN].append(user.as_dict(error_collector))
        return dictionary
