"""
ListModel implementations for accessing and manipulating Geometry models in QML

See http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing for guidance on how to develop these classes, including
what signals need to be emitted when changes to the data are made.
"""

from geometry_constructor.data_model import Vector, CylindricalGeometry, OFFGeometry
from nexusutils.readwriteoff import parse_off_file
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex, QUrl, Slot

from geometry_constructor.instrument_model import InstrumentModel


def change_value(item, attribute_name, value):
    """
    Updates the value of an items attribute
    :param item: the object having an attribute updated
    :param attribute_name: the name of the attribute to update
    :param value: the value to set the attribute to
    :return: whether the attribute value was changed
    """
    current_value = getattr(item, attribute_name)
    different = value != current_value
    if different:
        setattr(item, attribute_name, value)
    return different


class CylinderModel(QAbstractListModel):
    """
    A single item list model that allows properties of a Cylindrical geometry to be read and manipulated in QML
    """

    AxisXRole = Qt.UserRole + 100
    AxisYRole = Qt.UserRole + 101
    AxisZRole = Qt.UserRole + 102
    HeightRole = Qt.UserRole + 103
    RadiusRole = Qt.UserRole + 104

    def __init__(self):
        super().__init__()
        self.cylinder = CylindricalGeometry()

    def rowCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        properties = {
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
            CylinderModel.AxisXRole: [self.cylinder.axis_direction, 'x', value],
            CylinderModel.AxisYRole: [self.cylinder.axis_direction, 'y', value],
            CylinderModel.AxisZRole: [self.cylinder.axis_direction, 'z', value],
            CylinderModel.HeightRole: [self.cylinder, 'height', value],
            CylinderModel.RadiusRole: [self.cylinder, 'radius', value],
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
            CylinderModel.AxisXRole: b'axis_x',
            CylinderModel.AxisYRole: b'axis_y',
            CylinderModel.AxisZRole: b'axis_z',
            CylinderModel.HeightRole: b'cylinder_height',
            CylinderModel.RadiusRole: b'cylinder_radius'
        }

    def get_geometry(self):
        return self.cylinder

    @Slot(int, 'QVariant')
    def set_geometry(self, index, instrument: InstrumentModel):
        self.beginResetModel()
        self.cylinder = instrument.components[index].geometry
        self.endResetModel()


class OFFModel(QAbstractListModel):
    """
    A single item list model that allows properties of an OFF geometry to be read and manipulated in QML
    """

    FileNameRole = Qt.UserRole + 200
    VerticesRole = Qt.UserRole + 201
    FacesRole = Qt.UserRole + 202

    def __init__(self):
        super().__init__()
        self.geometry = OFFGeometry()
        self.file_url = QUrl('')

    def rowCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        properties = {
            OFFModel.FileNameRole: self.file_url,
            OFFModel.VerticesRole: self.geometry.vertices,
            OFFModel.FacesRole: self.geometry.faces,
        }
        if role in properties:
            return properties[role]

    def setData(self, index, value, role):
        changed = False
        param_options = {
            OFFModel.FileNameRole: [self, 'file_url', value],
            OFFModel.VerticesRole: [self.geometry, 'vertices', value],
            OFFModel.FacesRole: [self.geometry, 'faces', value],
        }
        if role in param_options:
            param_list = param_options[role]
            changed = change_value(*param_list)
        if role == OFFModel.FileNameRole:
            self.load_data()
            self.dataChanged.emit(index, index, [OFFModel.VerticesRole,
                                                 OFFModel.FacesRole])
        if changed:
            self.dataChanged.emit(index, index, role)
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {
            OFFModel.FileNameRole: b'file_url',
            OFFModel.VerticesRole: b'vertices',
            OFFModel.FacesRole: b'faces'
        }

    # Read the OFF file into self.geometry
    def load_data(self):
        filename = self.file_url.toString(options=QUrl.PreferLocalFile)
        with open(filename) as file:
            vertices, faces = parse_off_file(file)

        print(vertices)
        print(faces)

        self.geometry.vertices = [Vector(x, y, z) for x, y, z in (vertex for vertex in vertices)]
        self.geometry.faces = [face.tolist()[1:] for face in faces]

    def get_geometry(self):
        return self.geometry

    @Slot(int, 'QVariant')
    def set_geometry(self, index, instrument: InstrumentModel):
        self.beginResetModel()
        self.geometry = instrument.components[index].geometry
        self.endResetModel()
