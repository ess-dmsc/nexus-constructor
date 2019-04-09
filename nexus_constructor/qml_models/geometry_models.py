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
from nexus_constructor.qml_models import change_value
from PySide2.QtCore import Qt, QObject, QModelIndex, QUrl, Signal, Slot, Property
from PySide2.QtGui import QVector3D

from nexus_constructor.qml_models.instrument_model import InstrumentModel


class NoShapeModel(QObject):
    dataChanged = Signal()

    def __init__(self):
        super().__init__()
        self.geometry = NoShapeGeometry()

    def get_geometry(self):
        return self.geometry


class CylinderModel(QObject):
    """
    A single item list model that allows properties of a Cylindrical geometry to be read and manipulated in QML
    """

    dataChanged = Signal()

    def updateCylinder(self):
        self.cylinder = CylindricalGeometry(
            units=self.get_unit(),
            axis_direction=QVector3D(self.axis_x, self.axis_z, self.axis_y),
            height=self.get_cylinder_height(),
            radius=self.get_radius(),
        )
        self.dataChanged.emit()

    def get_unit(self):
        return self._unit

    def get_axis_x(self):
        return self._axis_x

    def get_axis_y(self):
        return self._axis_y

    def get_axis_z(self):
        return self._axis_z

    def get_cylinder_height(self):
        return self._cylinder_height

    def get_radius(self):
        return self._radius

    def set_unit(self, unit):
        self._unit = unit
        self.updateCylinder()

    def set_axis_x(self, axis):
        self._axis_x = axis
        self.updateCylinder()

    def set_axis_y(self, axis):
        self._axis_y = axis
        self.updateCylinder()

    def set_axis_z(self, axis):
        self._axis_z = axis
        self.updateCylinder()

    def set_cylinder_height(self, height):
        self._cylinder_height = height
        self.updateCylinder()

    def set_radius(self, radius):
        self._radius = radius
        self.updateCylinder()

    cylinder_units = Property(str, get_unit, set_unit, notify=dataChanged)
    axis_x = Property(int, get_axis_x, set_axis_x, notify=dataChanged)
    axis_y = Property(int, get_axis_y, set_axis_y, notify=dataChanged)
    axis_z = Property(int, get_axis_z, set_axis_z, notify=dataChanged)
    cylinder_height = Property(
        int, get_cylinder_height, set_cylinder_height, notify=dataChanged
    )
    cylinder_radius = Property(int, get_radius, set_radius, notify=dataChanged)

    def __init__(self):
        super().__init__()
        self.cylinder = CylindricalGeometry()
        self._unit = "m"
        self._axis_x = 1
        self._axis_y = 0
        self._axis_z = 0
        self._cylinder_height = 1
        self._radius = 1

    def get_geometry(self):
        return self.cylinder

    @Slot(int, "QVariant")
    def set_geometry(self, index, instrument: InstrumentModel):
        self.cylinder = instrument.components[index].geometry


class OFFModel(QObject):
    """
    A single item list model that allows properties of an OFFGeometry instance to be read and manipulated in QML
    """

    def __init__(self):
        super().__init__()
        self.geometry = OFFGeometry()

    _file = QUrl("")
    _units = "m"
    meshLoaded = Signal()

    dataChanged = Signal()

    def get_file(self):
        return self._file

    def get_units(self):
        return self._units

    def get_vertices(self):
        return self.geometry.vertices

    def get_faces(self):
        return self.geometry.faces

    def set_file(self, file):
        self._file = file
        self.load_data()

    def set_units(self, units):
        self._units = units

    def set_vertices(self, vertices):
        self.geometry.vertices = vertices

    def set_faces(self, faces):
        self.geometry.faces = faces

    file_url = Property(QUrl, get_file, set_file, notify=dataChanged)
    units = Property(str, get_units, set_units, notify=dataChanged)
    vertices = Property("QVariant", get_vertices, set_vertices, notify=dataChanged)
    faces = Property("QVariant", get_faces, set_faces, notify=dataChanged)

    def load_data(self):
        """Read the currently selected file into self.geometry"""
        filename = self._file.toString(
            options=QUrl.FormattingOptions(QUrl.PreferLocalFile)
        )
        load_geometry(filename, self.units, self.geometry)
        self.meshLoaded.emit()

    def get_geometry(self):
        return self.geometry

    @Slot(int, "QVariant")
    def set_geometry(self, index, instrument: InstrumentModel):
        self.geometry = instrument.components[index].geometry
