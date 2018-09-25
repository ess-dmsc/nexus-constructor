import attr
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex, Slot


@attr.s
class Pixel:
    name = attr.ib(str)
    faces = attr.ib(factory=list)


class PixelModel(QAbstractListModel):

    NameRole = Qt.UserRole + 1
    FacesRole = Qt.UserRole + 2

    def __init__(self):
        super().__init__()
        self.my_list = [Pixel(name='pixel1', faces=[1, 2, 3])]

    def rowCount(self, parent=QModelIndex()):
        return len(self.my_list)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == PixelModel.NameRole:
            return self.my_list[row].name
        if role == PixelModel.FacesRole:
            return self.my_list[row].faces

    def roleNames(self):
        return {
            PixelModel.NameRole: b'name',
            PixelModel.FacesRole: b'faces',
        }

    @Slot(str, str)
    def insert_pixel(self, name, faces):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.my_list.append(Pixel(name, [int(face) for face in faces.split(',')]))
        self.endInsertRows()

    @Slot(int)
    def remove_pixel(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        self.my_list = self.my_list[0:index] + self.my_list[index + 1:self.rowCount()]
        self.endRemoveRows()
