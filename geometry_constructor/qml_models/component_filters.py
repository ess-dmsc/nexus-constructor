"""
Filtered models for an instance of InstrumentModel
"""
from PySide2.QtCore import Property, QModelIndex, QSortFilterProxyModel, Signal


class InstrumentModelFilter(QSortFilterProxyModel):
    """Base class for filtering an InstrumentModel by a single index"""

    def __init__(self):
        super().__init__()
        self.desired_index = 0

    def get_index(self):
        return self.desired_index

    def set_index(self, val):
        self.desired_index = val
        print('setting index to:{}'.format(val))
        self.invalidateFilter()

    index_changed = Signal()

    index = Property(int, get_index, set_index, notify=index_changed)

    def get_model(self):
        return self.sourceModel()

    def set_model(self, val):
        self.setSourceModel(val)
        self.invalidateFilter()

    model_changed = Signal()

    model = Property('QVariant', get_model, set_model, notify=model_changed)


class SingleComponentModel(InstrumentModelFilter):
    """A filtered model that only displays a single component from an InstrumentModel"""

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        """Overrides filterAcceptsRow to only accept the component at the given index"""
        return source_row == self.index


class ExcludedComponentModel(InstrumentModelFilter):
    """A filtered model that displays all but one component from an InstrumentModel"""

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        """Overrides filterAcceptsRow to reject only the component at the given index"""
        return source_row != self.index
