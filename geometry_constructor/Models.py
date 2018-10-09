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
    TranslateVectorRole = Qt.UserRole + 2
    RotateAxisRole = Qt.UserRole + 3
    RotateAngleRole = Qt.UserRole + 4

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
        if role == InstrumentModel.TranslateVectorRole:
            return item.translate_vector
        if role == InstrumentModel.RotateAxisRole:
            return item.rotate_axis
        if role == InstrumentModel.RotateAngleRole:
            return item.rotate_angle

    def roleNames(self):
        return {
            InstrumentModel.NameRole: b'name',
            InstrumentModel.TranslateVectorRole: b'translate_vector',
            InstrumentModel.RotateAxisRole: b'rotate_axis',
            InstrumentModel.RotateAngleRole: b'rotate_angle',
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
