from typing import Callable, List, Union

from .component import Component
from .group import Group
from .module import StreamModules


class GroupContainer:
    def __init__(self, group: Union[Group, Component]):
        self._group = group
        self._possible_stream_modules = [module.value for module in StreamModules]

    @property
    def group(self) -> Union[Group, Component]:
        return self._group

    @group.setter
    def group(self, new_group: Union[Group, Component]):
        self._group = new_group

    def get_possible_stream_modules(self) -> List[str]:
        return self._possible_stream_modules

    def add_stream_module(self, module: str):
        self._modify_possible_streams(module, self._possible_stream_modules.append)

    def remove_stream_module(self, module: str):
        if module in self._possible_stream_modules:
            self._modify_possible_streams(module, self._possible_stream_modules.remove)

    def _modify_possible_streams(self, module: str, modify_list: Callable):
        if module in [StreamModules.EV42.value, StreamModules.EV44]:
            modify_list(StreamModules.EV42.value)
            modify_list(StreamModules.EV44.value)
        else:
            modify_list(module)
        self._possible_stream_modules = list(set(self._possible_stream_modules))
