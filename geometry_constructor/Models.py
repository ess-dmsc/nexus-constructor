import attr
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
    bottom = attr.ib(Vector)
    top = attr.ib(Vector)
    radius = attr.ib(int)


@attr.s
class OFFGeometry(Geometry):
    vertices = attr.ib(factory=list)
    faces = attr.ib(factory=list)
    winding_order = attr.ib(factory=list)


@attr.s
class Component:
    name = attr.ib(str)
    id = attr.ib(int)
    translate_vector = attr.ib(default=Vector(0, 0, 0))
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
                                        id=max(self.components, key=lambda x: x.id).id + 1,
                                        transform_parent_id=self.components[0].id))
        self.endInsertRows()

    @Slot(int)
    def remove_component(self, index):
        # Don't let the initial sample be removed
        if index == 0:
            return
        self.beginRemoveRows(QModelIndex(), index, index)
        self.components = self.components[0:index] + self.components[index + 1:self.rowCount()]
        self.endRemoveRows()
