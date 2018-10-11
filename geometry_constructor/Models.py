import attr
from enum import Enum
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex, Slot


def validate_nonzero_vector(instance, attribute, value):
    if value.x == 0 and value.y == 0 and value.z == 0:
        raise ValueError('Vector is zero length')


@attr.s
class Vector:
    x = attr.ib(float)
    y = attr.ib(float)
    z = attr.ib(float)


@attr.s
class Geometry:
    pass


@attr.s
class CylindricalGeometry(Geometry):
    bottom_center = attr.ib(Vector)
    top_center = attr.ib(Vector)
    bottom_edge = attr.ib(Vector)


@attr.s
class OFFGeometry(Geometry):
    vertices = attr.ib(factory=list)
    faces = attr.ib(factory=list)
    winding_order = attr.ib(factory=list)


@attr.s
class PixelData:
    pass


class CountDirection(Enum):
    ROW = 1
    COLUMN = 2


class Corner(Enum):
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


@attr.s
class PixelGrid(PixelData):
    rows = attr.ib(int)
    columns = attr.ib(int)
    row_height = attr.ib(float)
    col_width = attr.ib(float)
    first_id = attr.ib(int)
    count_direction = attr.ib(CountDirection)
    initial_count_corner = attr.ib(Corner)


@attr.s
class PixelMapping(PixelData):
    pixel_ids = attr.ib(list)  # pixel_ids[face_number] returns the pixel the face is part of, or None


@attr.s
class Component:
    name = attr.ib(str)
    id = attr.ib(int)
    translate_vector = attr.ib(default=Vector(0, 0, 0), type=Vector)
    rotate_axis = attr.ib(default=Vector(0, 0, 1), type=Vector, validator=validate_nonzero_vector)
    rotate_angle = attr.ib(default=0)
    transform_parent_id = attr.ib(default=None)
    geometry = attr.ib(default=None, type=Geometry)


@attr.s
class Sample(Component):
    pass


@attr.s
class Detector(Component):
    geometry = attr.ib(default=None, type=Geometry)
    pixel_data = attr.ib(default=None, type=PixelData)


class InstrumentModel(QAbstractListModel):

    NameRole = Qt.UserRole + 1
    TranslateVectorXRole = Qt.UserRole + 2
    TranslateVectorYRole = Qt.UserRole + 3
    TranslateVectorZRole = Qt.UserRole + 4
    RotateAxisXRole = Qt.UserRole + 5
    RotateAxisYRole = Qt.UserRole + 6
    RotateAxisZRole = Qt.UserRole + 7
    RotateAngleRole = Qt.UserRole + 8
    TransformParentIndexRole = Qt.UserRole + 9

    def __init__(self):
        super().__init__()
        self.components = [Sample(name='Sample', id=0)]

    def rowCount(self, parent=QModelIndex()):
        return len(self.components)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        item = self.components[row]
        if role == InstrumentModel.NameRole:
            return item.name
        if role == InstrumentModel.TranslateVectorXRole:
            return item.translate_vector.x
        if role == InstrumentModel.TranslateVectorYRole:
            return item.translate_vector.y
        if role == InstrumentModel.TranslateVectorZRole:
            return item.translate_vector.z
        if role == InstrumentModel.RotateAxisXRole:
            return item.rotate_axis.x
        if role == InstrumentModel.RotateAxisYRole:
            return item.rotate_axis.y
        if role == InstrumentModel.RotateAxisZRole:
            return item.rotate_axis.z
        if role == InstrumentModel.RotateAngleRole:
            return item.rotate_angle
        if role == InstrumentModel.TransformParentIndexRole:
            for i in range(len(self.components)):
                if self.components[i].id == item.transform_parent_id:
                    return i
            return 0

    # continue, referring to: http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing
    def setData(self, index, value, role):
        row = index.row()
        item = self.components[row]
        changed = False
        if role == InstrumentModel.NameRole:
            changed = item.name != value
            item.name = value
        elif role == InstrumentModel.TranslateVectorXRole:
            changed = item.translate_vector.x != value
            item.translate_vector.x = value
        elif role == InstrumentModel.TranslateVectorYRole:
            changed = item.translate_vector.y != value
            item.translate_vector.y = value
        elif role == InstrumentModel.TranslateVectorZRole:
            changed = item.translate_vector.z != value
            item.translate_vector.z = value
        elif role == InstrumentModel.RotateAxisXRole:
            changed = item.rotate_axis.x != value
            item.rotate_axis.x = value
        elif role == InstrumentModel.RotateAxisYRole:
            changed = item.rotate_axis.y != value
            item.rotate_axis.y = value
        elif role == InstrumentModel.RotateAxisZRole:
            changed = item.rotate_axis.z != value
            item.rotate_axis.z = value
        elif role == InstrumentModel.RotateAngleRole:
            changed = item.rotate_angle != value
            item.rotate_angle = value
        elif role == InstrumentModel.TransformParentIndexRole:
            parent_id = self.components[value].id
            if parent_id < 0:
                parent_id = 0
            changed = item.transform_parent_id != parent_id
            item.transform_parent_id = parent_id
        if changed:
            self.dataChanged.emit(index, index, role)
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {
            InstrumentModel.NameRole: b'name',
            InstrumentModel.TranslateVectorXRole: b'translate_x',
            InstrumentModel.TranslateVectorYRole: b'translate_y',
            InstrumentModel.TranslateVectorZRole: b'translate_z',
            InstrumentModel.RotateAxisXRole: b'rotate_x',
            InstrumentModel.RotateAxisYRole: b'rotate_y',
            InstrumentModel.RotateAxisZRole: b'rotate_z',
            InstrumentModel.RotateAngleRole: b'rotate_angle',
            InstrumentModel.TransformParentIndexRole: b'transform_parent_index'
        }

    @Slot(str)
    def add_detector(self, name):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.components.append(Detector(name=name,
                                        id=max(component.id for component in self.components) + 1,
                                        transform_parent_id=self.components[0].id,
                                        pixel_data=PixelGrid(rows=3, columns=4, row_height=0.1, col_width=0.3,
                                                             first_id=0, count_direction=CountDirection.ROW,
                                                             initial_count_corner=Corner.TOP_LEFT)))
        self.endInsertRows()

    @Slot(int)
    def remove_component(self, index):
        # Don't let the initial sample be removed
        if index == 0:
            return
        self.beginRemoveRows(QModelIndex(), index, index)
        self.components = self.components[0:index] + self.components[index + 1:self.rowCount()]
        self.endRemoveRows()
