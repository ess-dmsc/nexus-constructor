from nexus_constructor.common_attrs import CommonKeys, INSTRUMENT_NAME
from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group
from typing import Dict, Any

SAMPLE_NAME = "sample"


class Instrument(Group):
    def __init__(self, parent_node=None):
        super().__init__(name=INSTRUMENT_NAME, parent_node=parent_node)
        self.nx_class = "NXinstrument"

        self.sample = Component(SAMPLE_NAME, parent_node=self)
        self.sample.nx_class = "NXsample"
        self.component_list = [self.sample]

    def get_component_list(self):
        return self.component_list

    def add_component(self, component: Component):
        self.component_list.append(component)

    def remove_component(self, component: Component):
        self.component_list.remove(component)

    def as_dict(self) -> Dict[str, Any]:
        dictionary = super(Instrument, self).as_dict()
        # Put components (other than sample) in children
        dictionary[CommonKeys.CHILDREN].extend(
            [
                component.as_dict()
                for component in self.component_list
                if component.name != SAMPLE_NAME
            ]
        )
        return dictionary
