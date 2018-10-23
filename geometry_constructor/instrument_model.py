from geometry_constructor.data_model import Sample, Detector, PixelGrid, CountDirection, Corner, Vector,\
    CylindricalGeometry, OFFGeometry, Component
from geometry_constructor.off_renderer import OffMesh
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex, Slot


class InstrumentModel(QAbstractListModel):

    NameRole = Qt.UserRole + 1
    DescriptionRole = Qt.UserRole + 2
    TranslateVectorXRole = Qt.UserRole + 3
    TranslateVectorYRole = Qt.UserRole + 4
    TranslateVectorZRole = Qt.UserRole + 5
    RotateAxisXRole = Qt.UserRole + 6
    RotateAxisYRole = Qt.UserRole + 7
    RotateAxisZRole = Qt.UserRole + 8
    RotateAngleRole = Qt.UserRole + 9
    TransformParentIndexRole = Qt.UserRole + 10
    PixelDataRole = Qt.UserRole + 11
    GeometryRole = Qt.UserRole + 12
    MeshRole = Qt.UserRole + 13

    def __init__(self):
        super().__init__()
        self.components = [
            Sample(
                name='OFF Sample',
                geometry=OFFGeometry(
                    vertices=[Vector(x=-0.5, y=-0.5, z=0.5),
                              Vector(x=0.5, y=-0.5, z=0.5),
                              Vector(x=-0.5, y=0.5, z=0.5),
                              Vector(x=0.5, y=0.5, z=0.5),
                              Vector(x=-0.5, y=0.5, z=-0.5),
                              Vector(x=0.5, y=0.5, z=-0.5),
                              Vector(x=-0.5, y=-0.5, z=-0.5),
                              Vector(x=0.5, y=-0.5, z=-0.5)],
                    faces=[[0, 1, 3, 2],
                           [2, 3, 5, 4],
                           [4, 5, 7, 6],
                           [6, 7, 1, 0],
                           [1, 7, 5, 3],
                           [6, 0, 2, 4]]
                )),
            Detector(
                name='Cylinder Detector',
                geometry=CylindricalGeometry(radius=1, height=3),
                translate_vector=Vector(0, 3, 0)
            )]

    def rowCount(self, parent=QModelIndex()):
        return len(self.components)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        item = self.components[row]
        if role == InstrumentModel.NameRole:
            return item.name
        if role == InstrumentModel.DescriptionRole:
            return item.description
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
            if item.transform_parent in self.components:
                return self.components.index(item.transform_parent)
            return 0
        if role == InstrumentModel.PixelDataRole:
            if isinstance(item, Detector):
                return item.pixel_data
            return None
        if role == InstrumentModel.GeometryRole:
            return item.geometry
        if role == InstrumentModel.MeshRole:
            return self.generate_mesh(item)

    # continue, referring to: http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing
    def setData(self, index, value, role):
        row = index.row()
        item = self.components[row]
        changed = False
        if role == InstrumentModel.NameRole:
            changed = item.name != value
            item.name = value
        elif role == InstrumentModel.DescriptionRole:
            changed = item.description != value
            item.description = value
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
            if 0 <= value < len(self.components):
                selected = self.components[value]
            else:
                selected = None
            changed = item.transform_parent != selected
            item.transform_parent = selected
        if changed:
            self.dataChanged.emit(index, index, role)
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self):
        return {
            InstrumentModel.NameRole: b'name',
            InstrumentModel.DescriptionRole: b'description',
            InstrumentModel.TranslateVectorXRole: b'translate_x',
            InstrumentModel.TranslateVectorYRole: b'translate_y',
            InstrumentModel.TranslateVectorZRole: b'translate_z',
            InstrumentModel.RotateAxisXRole: b'rotate_x',
            InstrumentModel.RotateAxisYRole: b'rotate_y',
            InstrumentModel.RotateAxisZRole: b'rotate_z',
            InstrumentModel.RotateAngleRole: b'rotate_angle',
            InstrumentModel.TransformParentIndexRole: b'transform_parent_index',
            InstrumentModel.PixelDataRole: b'pixel_data',
            InstrumentModel.MeshRole: b'mesh'
        }

    @Slot(str)
    @Slot(str, str, int, float, float, float, float, float, float, float, 'QVariant')
    def add_detector(self, name, description, parent_index=0,
                     translate_x=0, translate_y=0, translate_z=0,
                     rotate_x=0, rotate_y=0, rotate_z=1, rotate_angle=0,
                     geometry_model=None):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        geometry = None if geometry_model is None else geometry_model.get_geometry()
        self.components.append(Detector(name=name,
                                        description=description,
                                        transform_parent=self.components[parent_index],
                                        translate_vector=Vector(translate_x, translate_y, translate_z),
                                        rotate_axis=Vector(rotate_x, rotate_y, rotate_z),
                                        rotate_angle=rotate_angle,
                                        geometry=geometry,
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

    @Slot(int, 'QVariant')
    def set_geometry(self, index, geometry_model):
        print(geometry_model)
        self.components[index].geometry = geometry_model.get_geometry()
        self.dataChanged.emit(index, index, [InstrumentModel.GeometryRole,
                                             InstrumentModel.MeshRole])

    def generate_mesh(self, component: Component):
        if isinstance(component.geometry, CylindricalGeometry):
            geometry = component.geometry.as_off_geometry()
        elif isinstance(component.geometry, OFFGeometry):
            geometry = component.geometry
        else:
            return
        if isinstance(component, Detector):
            return OffMesh(geometry, component.pixel_data)
        return OffMesh(geometry)
