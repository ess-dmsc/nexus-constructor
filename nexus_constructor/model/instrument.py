from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group


class Instrument(Group):
    def __init__(self):
        super().__init__("instrument")
        self.nx_class = "NXinstrument"

        sample = Component("sample")
        sample.nx_class = "NXsample"
        self.component_list = [sample]

    def get_component_list(self):
        return self.component_list

    def remove_component(self, component: Component):
        self.component_list.remove(component)
