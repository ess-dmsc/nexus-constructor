"""
ListModel implementations for accessing and manipulating Geometry qml_models in QML

See http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing for guidance on how to develop these classes, including
what signals need to be emitted when changes to the data are made.
"""

from nexus_constructor.geometry_types import (
    CylindricalGeometry,
    OFFGeometry,
    NoShapeGeometry,
)
from nexus_constructor.geometry_loader import load_geometry
from PySide2.QtCore import QObject, QUrl, Signal, Slot, Property
from nexus_constructor.qml_models.instrument_model import InstrumentModel


class NoShapeModel(QObject):
    """
    A single item model that allows properties of an object with no geometry to be read and manipulated in QML

    """

    dataChanged = Signal()

    def __init__(self):
        super().__init__()
        self.geometry = NoShapeGeometry()

    def get_geometry(self):
        return self.geometry


class CylinderModel(QObject):
    """
    A single item model that allows properties of a Cylindrical geometry to be read and manipulated in QML
    """

    dataChanged = Signal()

    def get_unit(self):
        return self.cylinder.units

    def get_axis_x(self):
        return self.cylinder.axis_direction.x()

    def get_axis_y(self):
        return self.cylinder.axis_direction.y()

    def get_axis_z(self):
        return self.cylinder.axis_direction.z()

    def get_cylinder_height(self):
        return self.cylinder.height

    def get_radius(self):
        return self.cylinder.radius

    def set_unit(self, unit):
        self.cylinder.units = unit

    def set_axis_x(self, axis):
        self.cylinder.axis_direction.setX(axis)

    def set_axis_y(self, axis):
        self.cylinder.axis_direction.setY(axis)

    def set_axis_z(self, axis):
        self.cylinder.axis_direction.setZ(axis)

    def set_cylinder_height(self, height):
        self.cylinder.height = height

    def set_radius(self, radius):
        self.cylinder.radius = radius

    cylinder_units = Property(str, get_unit, set_unit, notify=dataChanged)
    axis_x = Property(float, get_axis_x, set_axis_x, notify=dataChanged)
    axis_y = Property(float, get_axis_y, set_axis_y, notify=dataChanged)
    axis_z = Property(float, get_axis_z, set_axis_z, notify=dataChanged)
    cylinder_height = Property(
        float, get_cylinder_height, set_cylinder_height, notify=dataChanged
    )
    cylinder_radius = Property(float, get_radius, set_radius, notify=dataChanged)

    def __init__(self):
        super().__init__()
        self.cylinder = CylindricalGeometry()

    def get_geometry(self):
        return self.cylinder

    @Slot(int, "QVariant")
    def set_geometry(self, index, instrument: InstrumentModel):
        self.cylinder = instrument.components[index].geometry


class OFFModel(QObject):
    """
    A single item model that allows properties of an OFFGeometry instance to be read and manipulated in QML
    """

    _file = QUrl("")
    _units = "m"

    def __init__(self):
        super().__init__()
        self.geometry = OFFGeometry()

    dataChanged = Signal()

    def get_file(self):
        return self._file

    def get_units(self):
        return self._units

    def set_file(self, file):
        self._file = QUrl(file)
        self.load_data()

    def set_units(self, units):
        self._units = units

    file_url = Property(QUrl, get_file, set_file, notify=dataChanged)
    units = Property(str, get_units, set_units, notify=dataChanged)

    def load_data(self):
        """Read the currently selected file into self.geometry"""
        filename = self._file.toString(
            options=QUrl.FormattingOptions(QUrl.PreferLocalFile)
        )
        self.geometry = load_geometry(filename, self._units, self.geometry)
        self.dataChanged.emit()

    def get_geometry(self):
        return self.geometry

    @Slot(int, "QVariant")
    def set_geometry(self, index, instrument: InstrumentModel):
        self.geometry = instrument.components[index].geometry
        