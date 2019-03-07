"""
ListModel implementations for accessing and manipulating Geometry qml_models in QML

See http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing for guidance on how to develop these classes, including
what signals need to be emitted when changes to the data are made.
"""

from nexus_constructor.data_model import CylindricalGeometry, OFFGeometry
from nexus_constructor.geometry_loader import load_geometry
from nexus_constructor.qml_models import change_value
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex, QUrl, Signal, Slot

from nexus_constructor.qml_models.instrument_model import InstrumentModel


class CylinderModel(QAbstractListModel):
    """
    A single item list model that allows properties of a Cylindrical geometry to be read and manipulated in QML
    """

    UnitsRole = Qt.UserRole + 100
    AxisXRole = Qt.UserRole + 101
    AxisYRole = Qt.UserRole + 102
    AxisZRole = Qt.UserRole + 103
    HeightRole = Qt.UserRole + 104
    RadiusRole = Qt.UserRole + 105

    def __init__(self):
        super().__init__()
        self.cylinder = CylindricalGeometry()

    def rowCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        properties = {
            CylinderModel.UnitsRole: self.cylinder.units,
            CylinderModel.AxisXRole: self.cylinder.axis_direction.x,
            CylinderModel.AxisYRole: self.cylinder.axis_direction.y,
            CylinderModel.AxisZRole: self.cylinder.axis_direction.z,
            CylinderModel.HeightRole: self.cylinder.height,
            CylinderModel.RadiusRole: self.cylinder.radius,
        }
        if role in properties:
            return properties[role]

    def setData(self, index, value, role):
        changed = False
        param_options = {
            CylinderModel.UnitsRole: [self.cylinder, "units", value],
            CylinderModel.AxisXRole: [self.cylinder.axis_direction, "x", value],
            CylinderModel.AxisYRole: [self.cylinder.axis_direction, "y", value],
            CylinderModel.AxisZRole: [self.cylinder.axis_direction, "z", value],
            CylinderModel.HeightRole: [self.cylinder, "height", value],
            CylinderModel.RadiusRole: [self.cylinder, "radius", value],
        }

        if role in param_options:
            param_list = param_options[role]
            changed = change_value(*param_list)
        if changed:
            self.dataChanged.emit(index, index, role)
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {
            CylinderModel.UnitsRole: b"cylinder_units",
            CylinderModel.AxisXRole: b"axis_x",
            CylinderModel.AxisYRole: b"axis_y",
            CylinderModel.AxisZRole: b"axis_z",
            CylinderModel.HeightRole: b"cylinder_height",
            CylinderModel.RadiusRole: b"cylinder_radius",
        }

    def get_geometry(self):
        return self.cylinder

    @Slot(int, "QVariant")
    def set_geometry(self, index, instrument: InstrumentModel):
        self.beginResetModel()

        self.cylinder = instrument.components[index].geometry
        self.endResetModel()


class OFFModel(QAbstractListModel):
    """
    A single item list model that allows properties of an OFFGeometry instance to be read and manipulated in QML
    """

    FileNameRole = Qt.UserRole + 200
    UnitsRole = Qt.UserRole + 201
    VerticesRole = Qt.UserRole + 202
    FacesRole = Qt.UserRole + 203

    meshLoaded = Signal()

    def __init__(self):
        super().__init__()
        self.geometry = OFFGeometry()
        self.file_url = QUrl("")
        self.units = ""

    def rowCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        properties = {
            OFFModel.FileNameRole: self.file_url,
            OFFModel.UnitsRole: self.units,
            OFFModel.VerticesRole: self.geometry.vertices,
            OFFModel.FacesRole: self.geometry.faces,
        }
        if role in properties:
            return properties[role]

    def setData(self, index, value, role):
        changed = False
        param_options = {
            OFFModel.FileNameRole: [self, "file_url", value],
            OFFModel.UnitsRole: [self, "units", value],
            OFFModel.VerticesRole: [self.geometry, "vertices", value],
            OFFModel.FacesRole: [self.geometry, "faces", value],
        }

        if role in param_options:
            param_list = param_options[role]
            changed = change_value(*param_list)
        if role == OFFModel.FileNameRole:
            self.load_data()
        if changed:
            self.dataChanged.emit(index, index, role)
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {
            OFFModel.FileNameRole: b"file_url",
            OFFModel.UnitsRole: b"units",
            OFFModel.VerticesRole: b"vertices",
            OFFModel.FacesRole: b"faces",
        }

    def load_data(self):
        """Read the currently selected file into self.geometry"""
        filename = QUrl(self.file_url).toString(
            options=QUrl.FormattingOptions(QUrl.PreferLocalFile)
        )
        self.beginResetModel()
        load_geometry(filename, self.units, self.geometry)
        self.endResetModel()
        self.meshLoaded.emit()

    def get_geometry(self):
        return self.geometry

    @Slot(int, "QVariant")
    def set_geometry(self, index, instrument: InstrumentModel):
        self.beginResetModel()
        self.geometry = instrument.components[index].geometry
        self.endResetModel()
