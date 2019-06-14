"""
ListModel implementations for accessing and manipulating pixel data in QML

See http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing for guidance on how to develop these classes, including
what signals need to be emitted when changes to the data are made.
"""
from nexus_constructor.qml_models.geometry_models import OFFModel
from nexus_constructor.pixel_data import PixelMapping, PixelGrid, SinglePixelId
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from PySide2.QtCore import (
    Qt,
    QAbstractListModel,
    QModelIndex,
    Slot,
    Property,
    Signal,
    QObject,
)
from math import isnan


class PixelGridModel(QObject):
    """
    A single item model that allows a PixelGrid to be read and manipulated in QML
    """

    dataChanged = Signal()

    def get_rows(self):
        return self.pixel_grid.rows

    def set_rows(self, rows):
        self.pixel_grid.rows = rows

    def get_columns(self):
        return self.pixel_grid.columns

    def set_columns(self, columns):
        self.pixel_grid.columns = columns

    def get_row_height(self):
        return self.pixel_grid.row_height

    def set_row_height(self, height):
        self.pixel_grid.row_height = height

    def get_column_width(self):
        return self.pixel_grid.col_width

    def set_column_width(self, width):
        self.pixel_grid.col_width = width

    def get_first_id(self):
        return self.pixel_grid.first_id

    def set_first_id(self, first_id):
        self.pixel_grid.first_id = first_id

    def get_count_direction(self):
        return self.pixel_grid.count_direction

    def set_count_direction(self, direction):
        self.pixel_grid.count_direction = direction

    def get_initial_count_corner(self):
        return self.pixel_grid.initial_count_corner

    def set_initial_count_corner(self, corner):
        self.pixel_grid.initial_count_corner = corner

    rows = Property(int, get_rows, set_rows, notify=dataChanged)
    columns = Property(int, get_columns, set_columns, notify=dataChanged)
    row_height = Property(float, get_row_height, set_row_height, notify=dataChanged)
    column_width = Property(
        float, get_column_width, set_column_width, notify=dataChanged
    )
    first_id = Property(int, get_first_id, set_first_id, notify=dataChanged)
    count_direction = Property(
        "QVariant", get_count_direction, set_count_direction, notify=dataChanged
    )
    initial_count_corner = Property(
        "QVariant",
        get_initial_count_corner,
        set_initial_count_corner,
        notify=dataChanged,
    )

    def __init__(self):
        super().__init__()
        self.pixel_grid = PixelGrid()

    def get_pixel_model(self):
        return self.pixel_grid

    @Slot(int, "QVariant")
    def set_pixel_model(self, index, instrument: InstrumentModel):
        component = instrument.components[index]
        if isinstance(component.pixel_data, PixelGrid):
            self.pixel_grid = component.pixel_data
            self.dataChanged.emit()


class PixelMappingModel(QAbstractListModel):
    """A list model that allows for accessing and changing a PixelMappings face id to pixel id mappings in QML"""

    PixelIdRole = Qt.UserRole + 500

    def __init__(self):
        super().__init__()
        self.pixel_mapping = PixelMapping(pixel_ids=[])

    def rowCount(self, parent=QModelIndex()):
        return len(self.pixel_mapping.pixel_ids)

    def data(self, index, role=Qt.DisplayRole):
        if role == PixelMappingModel.PixelIdRole:
            row = index.row()
            return self.pixel_mapping.pixel_ids[row - 1]

    def setData(self, index, value, role):
        changed = False
        if role == PixelMappingModel.PixelIdRole:
            row = index.row()
            current_value = self.pixel_mapping.pixel_ids[row - 1]
            if current_value != value:
                self.pixel_mapping.pixel_ids[row - 1] = (
                    None if isnan(value) else int(value)
                )
                self.dataChanged.emit(index, index, role)
                changed = True
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {PixelMappingModel.PixelIdRole: b"pixel_id"}

    def get_pixel_model(self):
        return self.pixel_mapping

    @Slot(int, "QVariant")
    def set_pixel_model(self, index, instrument: InstrumentModel):
        component = instrument.components[index]
        if isinstance(component.pixel_data, PixelMapping):
            self.beginResetModel()
            self.pixel_mapping = component.pixel_data
            self.endResetModel()

    @Slot("QVariant")
    def restart_mapping(self, geometry_model):
        if isinstance(geometry_model, OFFModel):
            self.beginResetModel()
            self.pixel_mapping.pixel_ids = [
                None for _ in range(len(geometry_model.geometry.faces))
            ]
            self.endResetModel()


class SinglePixelModel(QObject):
    """
    A single item model that allows a SinglePixelId to be read and manipulated in QML
    """

    dataChanged = Signal()

    def get_pixel_id(self):
        return self.pixel_model.pixel_id

    def set_pixel_id(self, pixel_id):
        self.pixel_model.pixel_id = pixel_id

    pixel_id = Property(int, get_pixel_id, set_pixel_id, notify=dataChanged)

    def __init__(self):
        super().__init__()
        self.pixel_model = SinglePixelId(pixel_id=0)

    def get_pixel_model(self):
        return self.pixel_model

    @Slot(int, "QVariant")
    def set_pixel_model(self, index, instrument: InstrumentModel):
        component = instrument.components[index]
        if isinstance(component.pixel_data, SinglePixelId):
            self.pixel_model = component.pixel_data
            self.dataChanged.emit()
