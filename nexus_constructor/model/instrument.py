from typing import List

from nexus_constructor.common_attrs import INSTRUMENT_NAME
from nexus_constructor.component_type import COMPONENT_TYPES
from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group

SAMPLE_NAME = "sample"


class Instrument(Group):
    def __init__(self, parent_node=None):
        super().__init__(name=INSTRUMENT_NAME, parent_node=parent_node)
        self.nx_class = "NXinstrument"
        self.sample = Component(SAMPLE_NAME, parent_node=self)
        self.sample.nx_class = "NXsample"

    def get_components(self) -> List:
        component_list = []
        for child in self.children:
            if isinstance(child, Group) and child.nx_class in COMPONENT_TYPES:
                component_list.append(child)
        component_list.append(self.sample)
        return component_list
