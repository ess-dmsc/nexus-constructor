from .group import Group
from .component import Component
from typing import Union


class GroupContainer:
    def __init__(self, group: Union[Group, Component]):
        self._group = group

    @property
    def group(self) -> Union[Group, Component]:
        return self._group

    @group.setter
    def group(self, new_group: Union[Group, Component]):
        self._group = new_group
