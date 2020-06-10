from PySide2.QtCore import QObject, Signal
from typing import Dict, Any


class Signals(QObject):
    """
    Signals when model is updated, to trigger, for example, updating the 3D view
    """

    file_changed = Signal("QVariant")
    file_opened = Signal("QVariant")
    component_added = Signal(str, "QVariant", "QVariant")
    component_removed = Signal(str)
    transformation_changed = Signal()
    show_entries_dialog = Signal("QVariant", "QVariant")


class Model:
    def __init__(self, entry):
        self.signals = Signals()
        self.entry = entry

    def as_dict(self) -> Dict[str, Any]:
        return {"nexus_structure": {"children": [self.entry.as_dict()]}}
