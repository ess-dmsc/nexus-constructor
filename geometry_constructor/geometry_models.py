from geometry_constructor.data_model import Vector, CylindricalGeometry, OFFGeometry
from nexusutils.readwriteoff import parse_off_file
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex, QUrl


class CylinderModel(QAbstractListModel):

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
        if role == CylinderModel.AxisXRole:
            return self.cylinder.axis_direction.x
        if role == CylinderModel.AxisYRole:
            return self.cylinder.axis_direction.y
        if role == CylinderModel.AxisZRole:
            return self.cylinder.axis_direction.z
        if role == CylinderModel.HeightRole:
            return self.cylinder.height
        if role == CylinderModel.RadiusRole:
            return self.cylinder.radius

    # continue, referring to: http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing
    def setData(self, index, value, role):
        changed = False
        if role == CylinderModel.AxisXRole:
            changed = self.cylinder.axis_direction.x != value
            self.cylinder.axis_direction.x = value
        if role == CylinderModel.AxisYRole:
            changed = self.cylinder.axis_direction.y != value
            self.cylinder.axis_direction.y = value
        if role == CylinderModel.AxisZRole:
            changed = self.cylinder.axis_direction.z != value
            self.cylinder.axis_direction.z = value
        if role == CylinderModel.HeightRole:
            changed = self.cylinder.height != value
            self.cylinder.height = value
        if role == CylinderModel.RadiusRole:
            changed = self.cylinder.radius != value
            self.cylinder.radius = value
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


class OFFModel(QAbstractListModel):

    FileNameRole = Qt.UserRole + 200
    VerticesRole = Qt.UserRole + 201
    FacesRole = Qt.UserRole + 202
    WindingOrderRole = Qt.UserRole + 203

    def __init__(self):
        super().__init__()
        self.geometry = OFFGeometry()
        self.file_url = QUrl('')

    def rowCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if role == OFFModel.FileNameRole:
            return self.file_url
        if role == OFFModel.VerticesRole:
            return self.geometry.vertices
        if role == OFFModel.FacesRole:
            return self.geometry.faces
        if role == OFFModel.WindingOrderRole:
            return self.geometry.winding_order

    # continue, referring to: http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing
    def setData(self, index, value, role):
        changed = False
        if role == OFFModel.FileNameRole:
            changed = self.file_url != value
            self.file_url = value
            if changed:
                self.load_data()
                self.dataChanged.emit(index, index, [OFFModel.VerticesRole,
                                                     OFFModel.FacesRole,
                                                     OFFModel.WindingOrderRole])
        if role == OFFModel.VerticesRole:
            changed = self.geometry.vertices != value
            self.geometry.vertices = value
        if role == OFFModel.FacesRole:
            changed = self.geometry.faces != value
            self.geometry.faces = value
        if role == OFFModel.WindingOrderRole:
            changed = self.geometry.winding_order != value
            self.geometry.winding_order = value
        if changed:
            self.dataChanged.emit(index, index, role)
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {
            OFFModel.FileNameRole: b'file_url',
            OFFModel.VerticesRole: b'vertices',
            OFFModel.FacesRole: b'faces',
            OFFModel.WindingOrderRole: b'winding_order'
        }

    # Read the OFF file into self.geometry
    def load_data(self):
        filename = self.file_url.toString(options=QUrl.PreferLocalFile)
        with open(filename) as file:
            vertices, faces = parse_off_file(file)

        self.geometry.vertices = [Vector(x, y, z) for x, y, z in (vertex for vertex in vertices)]

        self.geometry.faces = [point for face in faces for point in face[1:]]

        face_sizes = [face[0] for face in faces]

        self.geometry.winding_order = [sum(face_sizes[0:i]) for i in range(len(faces))]

    def get_geometry(self):
        return self.geometry
