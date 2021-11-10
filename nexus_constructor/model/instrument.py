from typing import Any, Dict

from nexus_constructor.common_attrs import INSTRUMENT_NAME, CommonKeys
from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group

SAMPLE_NAME = "sample"


class Instrument(Group):
    def __init__(self, parent_node=None):
        super().__init__(name=INSTRUMENT_NAME, parent_node=parent_node)
        self.nx_class = "NXinstrument"

        self.sample = Component(SAMPLE_NAME, parent_node=self)
        self.sample.nx_class = "NXsample"
        self.component_list = [self.sample]

    def as_dict(self, error_collector) -> Dict[str, Any]:
        dictionary = super(Instrument, self).as_dict(error_collector)
        # Put components (other than sample) in children
        dictionary[CommonKeys.CHILDREN].extend(
            [
                component.as_dict(error_collector)
                for component in self.component_list
                if component.name != SAMPLE_NAME
            ]
        )
        return dictionary
