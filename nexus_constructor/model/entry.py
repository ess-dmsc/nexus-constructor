from copy import copy
from typing import Any, Dict, List, Tuple

from nexus_constructor.common_attrs import INSTRUMENT_NAME, CommonKeys
from nexus_constructor.model.group import Group
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.model.module import Dataset
from nexus_constructor.model.value_type import ValueTypes

NEXUS_TITLE_NAME = "title"
TITLE_PLACEHOLDER_VALUE = "$TITLE$"
TITLE_PLACEHOLDER = Dataset(
    parent_node=None,
    name=NEXUS_TITLE_NAME,
    values=TITLE_PLACEHOLDER_VALUE,
    type=ValueTypes.STRING,
)

NEXUS_EXP_ID_NAME = "experiment_identifier"
EXP_ID_PLACEHOLDER_VALUE = "$EXP_ID$"
EXP_ID_PLACEHOLDER = Dataset(
    parent_node=None,
    name=NEXUS_EXP_ID_NAME,
    values=EXP_ID_PLACEHOLDER_VALUE,
    type=ValueTypes.STRING,
)

USERS_PLACEHOLDER = "$USERS$"


class Entry(Group):
    def __init__(self):
        super().__init__(name="entry", parent_node=None)
        self.nx_class = "NXentry"
        self._users_placeholder = False

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

    @property
    def users(self) -> List[Dict[str, str]]:
        users = []
        for child in self.children:
            if isinstance(child, Group) and child.nx_class == "NXuser":
                users.append(self._extract_user_info(child))
        return users

    @users.setter
    def users(self, users: List[Dict[str, str]]):
        self._clear_all_users()
        for user in users:
            group = Group(name="temporary name", parent_node=self)
            group = self._create_user(group, user)
            self[group.name] = group

    @property
    def users_placeholder(self) -> bool:
        return self._users_placeholder

    @users_placeholder.setter
    def users_placeholder(self, enable: bool):
        self._users_placeholder = enable

    def _extract_user_info(self, group: Group) -> Dict[str, str]:
        return {
            ds.name: str(ds.values) for ds in group.children if isinstance(ds, Dataset)
        }

    def _create_user(self, group: Group, user_data: Dict[str, str]) -> Group:
        group.name = f"user_{user_data['name'].replace(' ', '')}"
        group.nx_class = "NXuser"
        for name, value in user_data.items():
            group.children.append(
                Dataset(
                    name=name, parent_node=group, type=ValueTypes.STRING, values=value
                )
            )
        return group

    def _clear_all_users(self):
        old_users = []
        for child in self.children:
            if isinstance(child, Group) and child.nx_class == "NXuser":
                old_users.append(child)
        for user in old_users:
            self.children.remove(user)
        return old_users

    def _read_dataset_property(self, name: str, value: str) -> Tuple[str, bool]:
        dataset = self[name]
        if dataset:
            return (
                dataset.values,
                True if dataset.values == value else False,
            )
        return "", False

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
        if self._users_placeholder:
            dictionary = self._insert_users_placeholder(error_collector)
        else:
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
        return dictionary

    def _insert_users_placeholder(self, error_collector):
        # Temporarily remove any users while the dictionary is generated
        users = self._clear_all_users()
        dictionary = super(Entry, self).as_dict(error_collector)
        dictionary["children"].append(USERS_PLACEHOLDER)
        for user in users:
            self.children.append(user)
        return dictionary
