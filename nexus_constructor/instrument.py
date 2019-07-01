import os
import h5py
from nexus_constructor.component_type import make_dictionary_of_class_definitions
from nexus_constructor.nexus import nexus_wrapper as nx
from nexus_constructor.component import ComponentModel

COMPONENTS_IN_ENTRY = ["NXmonitor", "NXsample"]


def _convert_name_with_spaces(component_name):
    return component_name.replace(" ", "_")


class Instrument:
    """
    This is the high level container for all application data,
    as much as possible lives in the in memory NeXus file which this class holds (via NexusWrapper)

    Existance of this class, rather than putting all this functionality in NexusWrapper avoids circular dependencies,
    for example between component and NexusWrapper
    """

    def __init__(self, nexus_file: nx.NexusWrapper):
        self.nexus = nexus_file
        _, self.nx_component_classes = make_dictionary_of_class_definitions(
            os.path.abspath(
                os.path.join(
                    os.path.realpath(__file__), os.pardir, os.pardir, "definitions"
                )
            )
        )

    def add_component(self, name: str, nx_class: str, description: str):
        """
        Creates a component group in a NeXus file
        :param name: Name of the component group to create
        :param nx_class: NX_class of the component group to create
        :param description: Description of the component
        :return Wrapper for added component
        """
        name = _convert_name_with_spaces(name)
        parent_group = self.nexus.instrument
        if nx_class in COMPONENTS_IN_ENTRY:
            parent_group = self.nexus.entry
        component_group = self.nexus.create_nx_group(name, nx_class, parent_group)
        component = ComponentModel(self.nexus, component_group)
        component.description = description
        return component

    def remove_component(self, component: ComponentModel):
        """
        Removes a component group from the NeXus file
        :param component: The component to be removed
        """
        self.nexus.delete_node(component.group)

    def get_component_list(self):
        component_list = []

        def find_components(_, node):
            if isinstance(node, h5py.Group):
                if "NX_class" in node.attrs.keys():
                    if node.attrs["NX_class"] in self.nx_component_classes:
                        component_list.append(ComponentModel(self.nexus, node))

        self.nexus.nexus_file.visititems(find_components)
        return component_list
