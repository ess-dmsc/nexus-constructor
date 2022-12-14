from typing import Any, Dict, List

from PySide6.QtCore import QModelIndex, QObject, Signal

from nexus_constructor.common_attrs import CommonKeys
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry


class Signals(QObject):
    """
    Signals when model is updated, to trigger, for example, updating the 3D view
    """

    file_changed = Signal("QVariant")
    file_opened = Signal("QVariant")
    component_added = Signal("QVariant")
    component_removed = Signal(str)
    transformation_changed = Signal()
    show_entries_dialog = Signal("QVariant", "QVariant")
    module_changed = Signal()
    group_edited = Signal(QModelIndex, bool)
    component_selected = Signal(str)
    entity_selected = Signal("QVariant")
    path_name_changed = Signal(str, str)


class Model:
    def __init__(self):
        self.signals = Signals()
        self.entry = Entry()
        self._components: Dict = {}

    def append_component(self, component: Component):
        self._components[component.absolute_path] = component

    def remove_component(self, component: Component):
        self._components.pop(component.absolute_path)

    def get_components(self):
        return [item for item in self._components.values()]

    def as_dict(self, error_collector: List[str]) -> Dict[str, Any]:
        return {CommonKeys.CHILDREN: [self.entry.as_dict(error_collector)]}

    def as_nexus(self, nexus_node, error_collector: List[str]):
        self.entry.as_nexus(nexus_node, error_collector)
