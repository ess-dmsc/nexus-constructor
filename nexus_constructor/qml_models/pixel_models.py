"""
ListModel implementations for accessing and manipulating pixel data in QML

See http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing for guidance on how to develop these classes, including
what signals need to be emitted when changes to the data are made.
"""
from nexus_constructor.qml_models.geometry_models import OFFModel
from nexus_constructor.data_model import (
    PixelMapping,
    PixelGrid,
    SinglePixelId,
    Corner,
    CountDirection,
)
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from nexus_constructor.qml_models import change_value
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex, Slot
from math import isnan


class PixelGridModel(QAbstractListModel):
    """
    A single item list model that allows properties of a PixelGrid to be read and manipulated in QML
    """

    RowsRole = Qt.UserRole + 400
    ColumnsRole = Qt.UserRole + 401
    RowHeightRole = Qt.UserRole + 402
    ColumnWidthRole = Qt.UserRole + 403
    FirstIdRole = Qt.UserRole + 404
    CountDirectionRole = Qt.UserRole + 405
    InitialCountCornerRole = Qt.UserRole + 406

    def __init__(self):
        super().__init__()
        self.pixel_grid = PixelGrid()

    def rowCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        properties = {
            PixelGridModel.RowsRole: self.pixel_grid.rows,
            PixelGridModel.ColumnsRole: self.pixel_grid.columns,
            PixelGridModel.RowHeightRole: self.pixel_grid.row_height,
            PixelGridModel.ColumnWidthRole: self.pixel_grid.col_width,
            PixelGridModel.FirstIdRole: self.pixel_grid.first_id,
            PixelGridModel.CountDirectionRole: self.pixel_grid.count_direction,
            PixelGridModel.InitialCountCornerRole: self.pixel_grid.initial_count_corner,
        }
        if role in properties:
            return properties[role]

    def setData(self, index, value, role):
        changed = False
        # lambda wrappings prevent casting errors when setting other types
        param_options = {
            PixelGridModel.RowsRole: lambda: [self.pixel_grid, "rows", int(value)],
            PixelGridModel.ColumnsRole: lambda: [
                self.pixel_grid,
                "columns",
                int(value),
            ],
            PixelGridModel.RowHeightRole: lambda: [
                self.pixel_grid,
                "row_height",
                value,
            ],
            PixelGridModel.ColumnWidthRole: lambda: [
                self.pixel_grid,
                "col_width",
                value,
            ],
            PixelGridModel.FirstIdRole: lambda: [
                self.pixel_grid,
                "first_id",
                int(value),
            ],
            PixelGridModel.CountDirectionRole: lambda: [
                self.pixel_grid,
                "count_direction",
                CountDirection[value],
            ],
            PixelGridModel.InitialCountCornerRole: lambda: [
                self.pixel_grid,
                "initial_count_corner",
                Corner[value],
            ],
        }
        if role in param_options:
            param_list = param_options[role]()
            changed = change_value(*param_list)
        if changed:
            self.dataChanged.emit(index, index, role)
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {
            PixelGridModel.RowsRole: b"rows",
            PixelGridModel.ColumnsRole: b"columns",
            PixelGridModel.RowHeightRole: b"row_height",
            PixelGridModel.ColumnWidthRole: b"col_width",
            PixelGridModel.FirstIdRole: b"first_id",
            PixelGridModel.CountDirectionRole: b"count_direction",
            PixelGridModel.InitialCountCornerRole: b"initial_count_corner",
        }

    def get_pixel_model(self):
        return self.pixel_grid

    @Slot(int, "QVariant")
    def set_pixel_model(self, index, instrument: InstrumentModel):
        component = instrument.components[index]
        if isinstance(component.pixel_data, PixelGrid):
            self.beginResetModel()
            self.pixel_grid = component.pixel_data
            self.endResetModel()


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
            return self.pixel_mapping.pixel_ids[row]

    def setData(self, index, value, role):
        changed = False
        if role == PixelMappingModel.PixelIdRole:
            row = index.row()
            current_value = self.pixel_mapping.pixel_ids[row]
            if current_value != value:
                self.pixel_mapping.pixel_ids[row] = None if isnan(value) else int(value)
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


class SinglePixelModel(QAbstractListModel):
    """
    A single item list model that allows properties of a SinglePixelId to be read and manipulated in QML
    """

    PixelIdRole = Qt.UserRole + 600

    def __init__(self):
        super().__init__()
        self.pixel_model = SinglePixelId(pixel_id=0)

    def rowCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if role == SinglePixelModel.PixelIdRole:
            return self.pixel_model.pixel_id

    def setData(self, index, value, role):
        changed = False
        if role == SinglePixelModel.PixelIdRole:
            current_value = self.pixel_model.pixel_id
            if current_value != value:
                self.pixel_model.pixel_id = None if isnan(value) else int(value)
                self.dataChanged.emit(index, index, role)
                changed = True
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {SinglePixelModel.PixelIdRole: b"pixel_id"}

    def get_pixel_model(self):
        return self.pixel_model

    @Slot(int, "QVariant")
    def set_pixel_model(self, index, instrument: InstrumentModel):
        component = instrument.components[index]
        if isinstance(component.pixel_data, SinglePixelId):
            self.beginResetModel()
            self.pixel_model = component.pixel_data
            self.endResetModel()
