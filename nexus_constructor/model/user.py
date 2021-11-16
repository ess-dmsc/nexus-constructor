from typing import List, Dict, Any

from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.group import Group
from nexus_constructor.model.value_type import ValueTypes


class User(Group):
    def __init__(self, nexus_name=None, parent_node=None, **user_data):
        name = (
            f"user_{user_data['name'].replace(' ', '')}"
            if not nexus_name
            else nexus_name
        )
        super().__init__(name=name, parent_node=parent_node)
        self.nx_class = "NXuser"
        for n, v in user_data.items():
            self.children.append(Dataset(name=n, type=ValueTypes.STRING, values=v))

    def as_dict(self, error_collector: List[str]) -> Dict[str, Any]:
        return super().as_dict(error_collector)

    def values_dict(self) -> Dict[str, str]:
        return {ds.name: ds.values for ds in self.children}
