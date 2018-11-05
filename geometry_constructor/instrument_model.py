from geometry_constructor.data_model import Sample, Detector, PixelGrid, CountDirection, Corner, Vector,\
    CylindricalGeometry, OFFGeometry, Component
from geometry_constructor.off_renderer import OffMesh
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex, Signal, Slot
from PySide2.QtGui import QMatrix4x4, QVector3D


class InstrumentModel(QAbstractListModel):
    """
    A model that provides QML access to a list of components and their properties

    When this class is exposed to Qt/Qml through a call to PySide2.QtQml.qmlRegisterType an instance of this object can
    be created in Qml and used as a model for components like a listview, with a repeated visual representation of each
    component in the model.
    Within a components section of qml, any string specified in the roleNames method will link to a property of the
    component through the mapped Role, and the 'data' and 'setData' methods.
    For example, the following qml snippet would show all the component names:

    ListView {
        width: 100; height: 200

        model: InstrumentModel {}
        delegate: Text {
            text: name
        }
    }

    Guidance on how to correctly extend QAbstractListModel, including method signatures and required signals can be
    found at http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing
    """

    model_updated = Signal('QVariant')

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
    TransformMatrixRole = Qt.UserRole + 14

    def __init__(self):
        super().__init__()

        self.dataChanged.connect(self.send_model_updated)
        self.rowsInserted.connect(self.send_model_updated)
        self.rowsRemoved.connect(self.send_model_updated)
        self.modelReset.connect(self.send_model_updated)

        self.components = [
            Sample(
                name='Sample',
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
                ))]
        self.meshes = [self.generate_mesh(component) for component in self.components]

    def rowCount(self, parent=QModelIndex()):
        return len(self.components)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        component = self.components[row]
        # lambdas prevent calculated properties from being generated each time any property is retrieved
        accessors = {
            InstrumentModel.NameRole: lambda: component.name,
            InstrumentModel.DescriptionRole: lambda: component.description,
            InstrumentModel.TranslateVectorXRole: lambda: component.translate_vector.x,
            InstrumentModel.TranslateVectorYRole: lambda: component.translate_vector.y,
            InstrumentModel.TranslateVectorZRole: lambda: component.translate_vector.z,
            InstrumentModel.RotateAxisXRole: lambda: component.rotate_axis.x,
            InstrumentModel.RotateAxisYRole: lambda: component.rotate_axis.y,
            InstrumentModel.RotateAxisZRole: lambda: component.rotate_axis.z,
            InstrumentModel.RotateAngleRole: lambda: component.rotate_angle,
            InstrumentModel.TransformParentIndexRole:
                lambda: self.components.index(component.transform_parent)
                if component.transform_parent in self.components
                else 0,
            InstrumentModel.PixelDataRole:
                lambda: component.pixel_data if isinstance(component, Detector) else None,
            InstrumentModel.GeometryRole: lambda: component.geometry,
            InstrumentModel.MeshRole: lambda: self.meshes[row],
            InstrumentModel.TransformMatrixRole: lambda: self.generate_matrix(component),
        }
        if role in accessors:
            return accessors[role]()

    def setData(self, index, value, role):
        row = index.row()
        item = self.components[row]
        changed = False
        # lambdas prevent non integer values indexing the components list
        param_options = {
            InstrumentModel.NameRole: lambda: [item, 'name', value, False],
            InstrumentModel.DescriptionRole: lambda: [item, 'description', value, False],
            InstrumentModel.TranslateVectorXRole: lambda: [item.translate_vector, 'x', value, True],
            InstrumentModel.TranslateVectorYRole: lambda: [item.translate_vector, 'y', value, True],
            InstrumentModel.TranslateVectorZRole: lambda: [item.translate_vector, 'z', value, True],
            InstrumentModel.RotateAxisXRole: lambda: [item.rotate_axis, 'x', value, True],
            InstrumentModel.RotateAxisYRole: lambda: [item.rotate_axis, 'y', value, True],
            InstrumentModel.RotateAxisZRole: lambda: [item.rotate_axis, 'z', value, True],
            InstrumentModel.RotateAngleRole: lambda: [item, 'rotate_angle', value, True],
            InstrumentModel.TransformParentIndexRole: lambda: [
                item,
                'transform_parent',
                self.components[value] if value in range(len(self.components)) else None,
                True,
            ],
        }
        if role in param_options:
            param_list = param_options[role]()
            changed = self.change_value(*param_list)
        if changed:
            self.dataChanged.emit(index, index, role)
        return changed

    def change_value(self, item, attribute_name, value, transforms):
        current_value = getattr(item, attribute_name)
        different = value != current_value
        if different:
            setattr(item, attribute_name, value)
            if transforms:
                self.update_child_transforms(item)
        return different

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
            InstrumentModel.MeshRole: b'mesh',
            InstrumentModel.TransformMatrixRole: b'transform_matrix',
        }

    @Slot(str)
    @Slot(str, str, int, float, float, float, float, float, float, float, 'QVariant')
    def add_detector(self, name, description='', parent_index=0,
                     translate_x=0, translate_y=0, translate_z=0,
                     rotate_x=0, rotate_y=0, rotate_z=1, rotate_angle=0,
                     geometry_model=None):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        geometry = None if geometry_model is None else geometry_model.get_geometry()
        detector = Detector(name=name,
                            description=description,
                            transform_parent=self.components[parent_index],
                            translate_vector=Vector(translate_x, translate_y, translate_z),
                            rotate_axis=Vector(rotate_x, rotate_y, rotate_z),
                            rotate_angle=rotate_angle,
                            geometry=geometry,
                            pixel_data=PixelGrid(rows=3, columns=4, row_height=2, col_width=3,
                                                 first_id=0, count_direction=CountDirection.ROW,
                                                 initial_count_corner=Corner.TOP_LEFT))
        self.components.append(detector)
        self.meshes.append(self.generate_mesh(detector))
        self.endInsertRows()

    @Slot(int)
    def remove_component(self, index):
        # Don't let the initial sample be removed
        if index == 0:
            return
        self.beginRemoveRows(QModelIndex(), index, index)
        self.components.pop(index)
        self.meshes.pop(index)
        self.endRemoveRows()

    @Slot(int, 'QVariant')
    def set_geometry(self, index, geometry_model):
        print(geometry_model)
        self.components[index].geometry = geometry_model.get_geometry()
        self.meshes[index] = self.generate_mesh(self.components[index])
        model_index = self.createIndex(index, 0)
        self.dataChanged.emit(model_index, model_index, [InstrumentModel.GeometryRole,
                                                         InstrumentModel.MeshRole])

    def send_model_updated(self):
        self.model_updated.emit(self)

    def replace_contents(self, components):
        self.beginResetModel()
        self.components = components
        self.meshes = [self.generate_mesh(component) for component in self.components]
        self.endResetModel()

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

    def generate_matrix(self, component: Component):
        matrix = QMatrix4x4()

        def apply_transforms(item: Component):
            if item.transform_parent is not None and item != item.transform_parent:
                apply_transforms(item.transform_parent)

            matrix.rotate(item.rotate_angle,
                          QVector3D(item.rotate_axis.x,
                                    item.rotate_axis.y,
                                    item.rotate_axis.z))
            matrix.translate(item.translate_vector.x,
                             item.translate_vector.y,
                             item.translate_vector.z)
        apply_transforms(component)
        return matrix

    def update_child_transforms(self, component):
        for i in range(len(self.components)):
            candidate = self.components[i]
            if candidate.transform_parent is component and candidate is not component:
                model_index = self.createIndex(i, 0)
                self.dataChanged.emit(model_index, model_index, InstrumentModel.TransformMatrixRole)
                self.update_child_transforms(candidate)
