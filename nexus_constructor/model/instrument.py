from typing import List

from nexus_constructor.common_attrs import INSTRUMENT_NAME
from nexus_constructor.component_type import SAMPLE_CLASS_NAME
from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group

SAMPLE_NAME = "sample"


class Instrument(Group):
    def __init__(self, parent_node=None):
        super().__init__(name=INSTRUMENT_NAME, parent_node=parent_node)
        self.nx_class = "NXinstrument"
        self.sample = Component(SAMPLE_NAME, parent_node=self)
        self.sample.nx_class = SAMPLE_CLASS_NAME

    def get_components(self) -> List:
        return self._get_nexus_instances(Component)

    def get_groups(self) -> List:
        return self._get_nexus_instances(Group)

    def _get_nexus_instances(self, nexus_type) -> List:
        nexus_list = []
        for child in self.children:
            if isinstance(child, nexus_type):
                nexus_list.append(child)
        nexus_list.append(self.sample)
        return nexus_list
