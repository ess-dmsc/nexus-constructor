from geometry_constructor.data_model import Sample, Detector, Monitor, PixelGrid, PixelMapping, Vector,\
    CylindricalGeometry, OFFGeometry, Component
from geometry_constructor.off_renderer import OffMesh
from PySide2.QtCore import Property, Qt, QAbstractListModel, QModelIndex, QSortFilterProxyModel, Signal, Slot
from PySide2.QtGui import QMatrix4x4, QVector3D
import re


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
    PixelStateRole = Qt.UserRole + 11
    GeometryStateRole = Qt.UserRole + 12
    MeshRole = Qt.UserRole + 13
    TransformMatrixRole = Qt.UserRole + 14
    RemovableRole = Qt.UserRole + 15

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
            InstrumentModel.PixelStateRole: lambda: self.determine_pixel_state(component),
            InstrumentModel.GeometryStateRole: lambda: self.determine_geometry_state(component),
            InstrumentModel.MeshRole: lambda: self.generate_mesh(component),
            InstrumentModel.TransformMatrixRole: lambda: self.generate_matrix(component),
            InstrumentModel.RemovableRole: lambda: self.is_removable(row),
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
            changed = self.change_value(item, *param_list)
        if changed:
            self.dataChanged.emit(index, index, role)
            if role == InstrumentModel.TransformParentIndexRole:
                self.update_removable()
        return changed

    def change_value(self, component, item, attribute_name, value, transforms):
        current_value = getattr(item, attribute_name)
        different = value != current_value
        if different:
            setattr(item, attribute_name, value)
            if transforms:
                self.update_child_transforms(component)
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
            InstrumentModel.PixelStateRole: b'pixel_state',
            InstrumentModel.GeometryStateRole: b'geometry_state',
            InstrumentModel.MeshRole: b'mesh',
            InstrumentModel.TransformMatrixRole: b'transform_matrix',
            InstrumentModel.RemovableRole: b'removable'
        }

    @Slot(str)
    @Slot(str, str, int, float, float, float, float, float, float, float, 'QVariant', 'QVariant')
    def add_detector(self, name, description='', parent_index=0,
                     translate_x=0, translate_y=0, translate_z=0,
                     rotate_x=0, rotate_y=0, rotate_z=1, rotate_angle=0,
                     geometry_model=None,
                     pixel_model=None):
        geometry = None if geometry_model is None else geometry_model.get_geometry()
        pixels = None if pixel_model is None else pixel_model.get_pixel_model()
        detector = Detector(name=name,
                            description=description,
                            transform_parent=self.components[parent_index],
                            translate_vector=Vector(translate_x, translate_y, translate_z),
                            rotate_axis=Vector(rotate_x, rotate_y, rotate_z),
                            rotate_angle=rotate_angle,
                            geometry=geometry,
                            pixel_data=pixels)
        self.add_component(detector)

    @Slot(str, int, float, float, float, float, float, float, float, 'QVariant', 'QVariant')
    def add_monitor(self, name, parent_index=0,
                    translate_x=0, translate_y=0, translate_z=0,
                    rotate_x=0, rotate_y=0, rotate_z=1, rotate_angle=0,
                    geometry_model=None,
                    pixel_model=None):
        geometry = None if geometry_model is None else geometry_model.get_geometry()
        pixel_data = None if pixel_model is None else pixel_model.get_pixel_model()
        monitor = Monitor(name=name,
                          transform_parent=self.components[parent_index],
                          translate_vector=Vector(translate_x, translate_y, translate_z),
                          rotate_axis=Vector(rotate_x, rotate_y, rotate_z),
                          rotate_angle=rotate_angle,
                          geometry=geometry,
                          pixel_data=pixel_data)
        self.add_component(monitor)

    def add_component(self, component: Component):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.components.append(component)
        self.endInsertRows()
        self.update_removable()

    @Slot(int)
    def remove_component(self, index):
        if self.is_removable(index):
            self.beginRemoveRows(QModelIndex(), index, index)
            self.components.pop(index)
            self.endRemoveRows()
            self.update_removable()

    @Slot(int, 'QVariant')
    def set_geometry(self, index, geometry_model):
        print(geometry_model)
        self.components[index].geometry = geometry_model.get_geometry()
        model_index = self.createIndex(index, 0)
        self.dataChanged.emit(model_index, model_index, [InstrumentModel.GeometryStateRole,
                                                         InstrumentModel.MeshRole])

    def send_model_updated(self):
        self.model_updated.emit(self)

    def replace_contents(self, components):
        self.beginResetModel()
        self.components = components
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

    @Slot(str, result=str)
    def generate_component_name(self, base):
        """Generates a unique name for a new component using a common base string"""
        regex = '^{}\d*$'.format(re.escape(base))
        similar_names = [component.name for component in self.components if re.match(regex, component.name)]

        if len(similar_names) == 0 or base not in similar_names:
            return base
        if similar_names == [base]:
            return base + '1'
        # find the highest number in use, and go one higher
        tailing_numbers = [int(name[len(base):]) for name in similar_names if name != base]
        return base + str(max(tailing_numbers) + 1)

    def is_removable(self, index: int):
        """
        Determine if a component can be removed from the model

        The initial sample should never be removable, and neither should transform parents of other components.
        """
        if index == 0:
            return False
        component = self.components[index]
        return len([c for c in self.components if c.transform_parent is component and c is not component]) == 0

    def update_removable(self):
        self.dataChanged.emit(self.createIndex(0, 0),
                              self.createIndex(len(self.components), 0),
                              InstrumentModel.RemovableRole)

    @staticmethod
    def determine_pixel_state(component):
        """Returns a string identifying the state a PixelControls editor should be in for the given component"""
        if isinstance(component, Detector):
            if isinstance(component.pixel_data, PixelGrid):
                return "Grid"
            elif isinstance(component.pixel_data, PixelMapping):
                return "Mapping"
        elif isinstance(component, Monitor):
            return "SinglePixel"
        return ""

    @staticmethod
    def determine_geometry_state(component):
        """Returns a string identifying the state a GeometryControls editor should be in for the given component"""
        if isinstance(component.geometry, CylindricalGeometry):
            return "Cylinder"
        elif isinstance(component.geometry, OFFGeometry):
            return "OFF"
        return ""

    @Slot(int)
    def update_mesh(self, index: int):
        """
        Slot to be called when another model updates properties that require a component's mesh to be updated

        :param index: The index in this model of the component needing it's mesh updated
        """
        model_index = self.createIndex(index, 0)
        self.dataChanged.emit(model_index, model_index, InstrumentModel.MeshRole)


class SingleComponentModel(QSortFilterProxyModel):
    """A filtered model that only displays a single component from an InstrumentModel"""

    def __init__(self):
        super().__init__()
        self.desired_index = 0

    def get_index(self):
        return self.desired_index

    def set_index(self, val):
        self.desired_index = val
        self.invalidateFilter()

    index_changed = Signal()

    index = Property(int, get_index, set_index, notify=index_changed)

    def get_model(self):
        return self.sourceModel()

    def set_model(self, val):
        self.setSourceModel(val)
        self.invalidateFilter()

    model_changed = Signal()

    model = Property('QVariant', get_model, set_model, notify=model_changed)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        """Overrides filterAcceptsRow to only accept the component at the given index"""
        return source_row == self.desired_index
