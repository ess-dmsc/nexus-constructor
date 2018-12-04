from PySide2.QtCore import QAbstractListModel, Qt, QModelIndex, Signal, Slot
from geometry_constructor.data_model import Transformation, Translation, Rotation
from geometry_constructor.qml_models import change_value, generate_unique_name


class TransformationModel(QAbstractListModel):
    """
    A listview model for a component's transform list

    Guidance on how to correctly extend QAbstractListModel, including method signatures and required signals can be
    found at http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing
    """

    TransformTypeRole = Qt.UserRole + 700
    TransformNameRole = Qt.UserRole + 701
    DeletableRole = Qt.UserRole + 702
    TranslateXRole = Qt.UserRole + 720
    TranslateYRole = Qt.UserRole + 721
    TranslateZRole = Qt.UserRole + 722
    RotateXRole = Qt.UserRole + 750
    RotateYRole = Qt.UserRole + 751
    RotateZRole = Qt.UserRole + 752
    RotateAngleRole = Qt.UserRole + 753

    transformsUpdated = Signal()

    def __init__(self, transforms: list=None):
        super().__init__()
        self.transforms = [] if transforms is None else transforms
        self.deletable = [True for _ in self.transforms]

    def rowCount(self, parent=QModelIndex()):
        return len(self.transforms)

    def data(self, index, role=Qt.DisplayRole):
        transform = self.transforms[index.row()]
        if isinstance(transform, Translation):
            properties = {
                TransformationModel.TransformTypeRole: 'Translate',
                TransformationModel.TransformNameRole: transform.name,
                TransformationModel.DeletableRole: self.deletable[index.row()],
                TransformationModel.TranslateXRole: transform.vector.x,
                TransformationModel.TranslateYRole: transform.vector.y,
                TransformationModel.TranslateZRole: transform.vector.z,
            }
        elif isinstance(transform, Rotation):
            properties = {
                TransformationModel.TransformTypeRole: 'Rotate',
                TransformationModel.TransformNameRole: transform.name,
                TransformationModel.DeletableRole: self.deletable[index.row()],
                TransformationModel.RotateXRole: transform.axis.x,
                TransformationModel.RotateYRole: transform.axis.y,
                TransformationModel.RotateZRole: transform.axis.z,
                TransformationModel.RotateAngleRole: transform.angle,
            }
        else:
            properties = {}
        if role in properties:
            return properties[role]
        else:
            return ''

    def setData(self, index, value, role):
        changed = False
        transform = self.transforms[index.row()]

        if isinstance(transform, Translation):
            param_options = {
                TransformationModel.TransformNameRole: [transform, 'name', value],
                TransformationModel.TranslateXRole: [transform.vector, 'x', value],
                TransformationModel.TranslateYRole: [transform.vector, 'y', value],
                TransformationModel.TranslateZRole: [transform.vector, 'z', value],
            }
        elif isinstance(transform, Rotation):
            param_options = {
                TransformationModel.TransformNameRole: [transform, 'name', value],
                TransformationModel.RotateXRole: [transform.axis, 'x', value],
                TransformationModel.RotateYRole: [transform.axis, 'y', value],
                TransformationModel.RotateZRole: [transform.axis, 'z', value],
                TransformationModel.RotateAngleRole: [transform, 'angle', value],
            }
        else:
            param_options = {}

        if role in param_options:
            param_list = param_options[role]
            changed = change_value(*param_list)
        if changed:
            self.dataChanged.emit(index, index, role)
            if role != TransformationModel.DeletableRole:
                self.transformsUpdated.emit()
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {
            TransformationModel.TransformTypeRole: b'transform_type',
            TransformationModel.TransformNameRole: b'name',
            TransformationModel.DeletableRole: b'deletable',
            TransformationModel.TranslateXRole: b'translate_x',
            TransformationModel.TranslateYRole: b'translate_y',
            TransformationModel.TranslateZRole: b'translate_z',
            TransformationModel.RotateXRole: b'rotate_x',
            TransformationModel.RotateYRole: b'rotate_y',
            TransformationModel.RotateZRole: b'rotate_z',
            TransformationModel.RotateAngleRole: b'rotate_angle',
        }

    @Slot()
    def add_translate(self):
        self.add_transform(Translation(name=generate_unique_name('Translate', self.transforms)))

    @Slot()
    def add_rotate(self):
        self.add_transform(Rotation(name=generate_unique_name('Rotate', self.transforms)))

    @Slot(int)
    def delete_transform(self, index: int):
        if self.deletable[index]:
            self.beginRemoveRows(QModelIndex(), index, index)
            self.transforms.pop(index)
            self.deletable.pop(index)
            self.endRemoveRows()
            self.transformsUpdated.emit()

    @Slot(int, int)
    def change_position(self, index: int, new_index: int):
        if new_index in range(self.rowCount()) and index in range(self.rowCount()):
            self.beginRemoveRows(QModelIndex(), index, index)
            transform = self.transforms.pop(index)
            deletable = self.deletable.pop(index)
            self.endRemoveRows()

            self.beginInsertRows(QModelIndex(), new_index, new_index)
            self.transforms.insert(new_index, transform)
            self.deletable.insert(new_index, deletable)
            self.endInsertRows()
            self.transformsUpdated.emit()

    def add_transform(self, transform: Transformation):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.transforms.append(transform)
        self.deletable.append(True)
        self.endInsertRows()
        self.transformsUpdated.emit()

    def reset_deletable(self):
        self.deletable = [True for _ in self.transforms]
        self.dataChanged.emit(
            self.createIndex(0, 0),
            self.createIndex(self.rowCount(), 0),
            TransformationModel.DeletableRole
        )

    def set_deletable(self, index: int, deletable: bool):
        if index in range(self.rowCount()):
            self.deletable[index] = deletable
            model_index = self.createIndex(index, 0)
            self.dataChanged.emit(model_index, model_index, TransformationModel.DeletableRole)
