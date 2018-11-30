from PySide2.QtCore import QAbstractListModel, Qt, QModelIndex, Signal, Slot
from geometry_constructor.data_model import Transformation, Translation, Rotation
from geometry_constructor.models import change_value
from geometry_constructor.instrument_model import InstrumentModel


class TransformationModel(QAbstractListModel):
    """
    A listview model for a component's transform list

    The component should be set using the set_component slot

    Guidance on how to correctly extend QAbstractListModel, including method signatures and required signals can be
    found at http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing
    """

    TransformTypeRole = Qt.UserRole + 700
    TranslateXRole = Qt.UserRole + 701
    TranslateYRole = Qt.UserRole + 702
    TranslateZRole = Qt.UserRole + 703
    RotateXRole = Qt.UserRole + 750
    RotateYRole = Qt.UserRole + 751
    RotateZRole = Qt.UserRole + 752
    RotateAngleRole = Qt.UserRole + 753

    transformsUpdated = Signal(int)

    def __init__(self):
        super().__init__()
        self.component_index = -1
        self.transforms = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.transforms)

    def data(self, index, role=Qt.DisplayRole):
        transform = self.transforms[index.row()]
        if isinstance(transform, Translation):
            properties = {
                TransformationModel.TransformTypeRole: 'Translate',
                TransformationModel.TranslateXRole: transform.vector.x,
                TransformationModel.TranslateYRole: transform.vector.y,
                TransformationModel.TranslateZRole: transform.vector.z,
            }
        elif isinstance(transform, Rotation):
            properties = {
                TransformationModel.TransformTypeRole: 'Rotate',
                TransformationModel.RotateXRole: transform.axis.x,
                TransformationModel.RotateYRole: transform.axis.y,
                TransformationModel.RotateZRole: transform.axis.z,
                TransformationModel.RotateAngleRole: transform.angle,
            }
        else:
            properties = {}
        if role in properties:
            return properties[role]

    def setData(self, index, value, role):
        changed = False
        transform = self.transforms[index.row()]

        if isinstance(transform, Translation):
            param_options = {
                TransformationModel.TranslateXRole: [transform.vector, 'x', value],
                TransformationModel.TranslateYRole: [transform.vector, 'y', value],
                TransformationModel.TranslateZRole: [transform.vector, 'z', value],
            }
        elif isinstance(transform, Rotation):
            param_options = {
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
            self.transformsUpdated.emit(self.component_index)
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {
            TransformationModel.TransformTypeRole: b'transform_type',
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
        self.add_transform(Translation())

    @Slot()
    def add_rotate(self):
        self.add_transform(Rotation())

    @Slot(int)
    def delete_transform(self, index: int):
        self.beginRemoveRows(QModelIndex(), index, index)
        self.transforms.pop(index)
        self.endRemoveRows()
        self.transformsUpdated.emit(self.component_index)

    @Slot(int, int)
    def change_position(self, index: int, new_index: int):
        if new_index in range(self.rowCount()) and index in range(self.rowCount()):
            self.beginRemoveRows(QModelIndex(), index, index)
            transform = self.transforms.pop(index)
            self.endRemoveRows()

            self.beginInsertRows(QModelIndex(), new_index, new_index)
            self.transforms.insert(new_index, transform)
            self.endInsertRows()
            self.transformsUpdated.emit(self.component_index)

    def add_transform(self, transform: Transformation):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.transforms.append(transform)
        self.endInsertRows()
        self.transformsUpdated.emit(self.component_index)

    @Slot(int, 'QVariant')
    def set_component(self, component_index: int, instrument: InstrumentModel):
        print("setting transform model component index to: {}".format(component_index))
        self.beginResetModel()
        self.component_index = component_index
        if component_index in range(instrument.rowCount()):
            self.transforms = instrument.components[component_index].transforms
        else:
            self.transforms = []
        self.endResetModel()
