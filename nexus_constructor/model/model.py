from typing import Any, Dict, List

from PySide2.QtCore import QObject, Signal

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


class Model:
    def __init__(self):
        self.signals = Signals()
        self.entry = Entry()
        self._components: List = []

    def append_component(self, component: Component):
        self._components.append(component)

    def get_components(self):
        return self._components

    def as_dict(self, error_collector: List[str]) -> Dict[str, Any]:
        return {CommonKeys.CHILDREN: [self.entry.as_dict(error_collector)]}
