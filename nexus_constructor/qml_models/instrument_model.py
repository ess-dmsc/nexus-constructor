from nexus_constructor.data_model import (
    ComponentType,
    PixelGrid,
    PixelMapping,
    CylindricalGeometry,
    OFFGeometry,
    NoShapeGeometry,
    Component,
    Rotation,
    Translation,
    OFFCube,
)
from nexus_constructor.qml_models import change_value, generate_unique_name
from nexus_constructor.qml_models.transform_model import TransformationModel
from nexus_constructor.off_renderer import OffMesh
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex, Signal, Slot
from PySide2.QtGui import QMatrix4x4, QVector3D


def generate_mesh(component: Component):
    if component.component_type == ComponentType.DETECTOR:
        return OffMesh(component.geometry.off_geometry, component.pixel_data)
    else:
        return OffMesh(component.geometry.off_geometry)


def determine_pixel_state(component):
    """Returns a string identifying the state a PixelControls editor should be in for the given component"""
    if component.component_type == ComponentType.DETECTOR:
        if isinstance(component.pixel_data, PixelGrid):
            return "Grid"
        elif isinstance(component.pixel_data, PixelMapping):
            return "Mapping"
    elif component.component_type == ComponentType.MONITOR:
        return "SinglePixel"
    return ""


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

    model_updated = Signal("QVariant")

    NameRole = Qt.UserRole + 1
    DescriptionRole = Qt.UserRole + 2
    TransformParentIndexRole = Qt.UserRole + 3
    DependentTransformIndexRole = Qt.UserRole + 4
    PixelStateRole = Qt.UserRole + 5
    GeometryStateRole = Qt.UserRole + 6
    MeshRole = Qt.UserRole + 7
    TransformMatrixRole = Qt.UserRole + 8
    RemovableRole = Qt.UserRole + 9
    TransformModelRole = Qt.UserRole + 10

    def __init__(self):
        super().__init__()

        self.dataChanged.connect(self.send_model_updated)
        self.rowsInserted.connect(self.send_model_updated)
        self.rowsRemoved.connect(self.send_model_updated)
        self.modelReset.connect(self.send_model_updated)

        self.components = [
            Component(
                component_type=ComponentType.SAMPLE, name="Sample", geometry=OFFCube
            )
        ]
        self.transform_models = [
            TransformationModel(component.transforms) for component in self.components
        ]

    def rowCount(self, parent=QModelIndex()):
        return len(self.components)

    def data(self, index, role=Qt.DisplayRole):

        row = index.row()
        component = self.components[row]
        # lambdas prevent calculated properties from being generated each time any property is retrieved
        accessors = {
            InstrumentModel.NameRole: lambda: component.name,
            InstrumentModel.DescriptionRole: lambda: component.description,
            InstrumentModel.TransformParentIndexRole: lambda: self.components.index(
                component.transform_parent
            )
            if component.transform_parent in self.components
            else 0,
            InstrumentModel.DependentTransformIndexRole: lambda: component.transform_parent.transforms.index(
                component.dependent_transform
            )
            if component.transform_parent is not None
            and component.dependent_transform in component.transform_parent.transforms
            else -1,
            InstrumentModel.PixelStateRole: lambda: determine_pixel_state(component),
            InstrumentModel.GeometryStateRole: lambda: component.geometry.geometry_str,
            InstrumentModel.MeshRole: lambda: generate_mesh(component),
            InstrumentModel.TransformMatrixRole: lambda: self.generate_matrix(
                component
            ),
            InstrumentModel.RemovableRole: lambda: self.is_removable(row),
            InstrumentModel.TransformModelRole: lambda: self.transform_models[row],
        }
        if role in accessors:
            return accessors[role]()

    def roleNames(self):
        return {
            InstrumentModel.NameRole: b"name",
            InstrumentModel.DescriptionRole: b"description",
            InstrumentModel.TransformParentIndexRole: b"transform_parent_index",
            InstrumentModel.DependentTransformIndexRole: b"dependent_transform_index",
            InstrumentModel.PixelStateRole: b"pixel_state",
            InstrumentModel.GeometryStateRole: b"geometry_state",
            InstrumentModel.MeshRole: b"mesh",
            InstrumentModel.TransformMatrixRole: b"transform_matrix",
            InstrumentModel.RemovableRole: b"removable",
            InstrumentModel.TransformModelRole: b"transform_model",
        }

    def setData(self, index, value, role):
        row = index.row()
        item = self.components[row]
        changed = False
        # lambdas prevent non integer values indexing the components list
        param_options = {
            InstrumentModel.NameRole: lambda: [item, "name", value],
            InstrumentModel.DescriptionRole: lambda: [item, "description", value],
            InstrumentModel.TransformParentIndexRole: lambda: [
                item,
                "transform_parent",
                self.components[value]
                if value in range(len(self.components))
                else None,
            ],
            InstrumentModel.DependentTransformIndexRole: lambda: [
                item,
                "dependent_transform",
                item.transform_parent.transforms[value]
                if value in range(len(item.transform_parent.transforms))
                else None,
            ],
        }
        if role in param_options:
            param_list = param_options[role]()
            changed = change_value(*param_list)
        if changed:
            if role == InstrumentModel.TransformParentIndexRole:
                self.setData(index, -1, InstrumentModel.DependentTransformIndexRole)
                self.update_removable()
                self.update_child_transforms(item)
                self.update_transforms_deletable()
            if role == InstrumentModel.DependentTransformIndexRole:
                self.update_child_transforms(item)
                self.update_transforms_deletable()
            self.dataChanged.emit(index, index, role)
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    @Slot(str, str, str, int, int, "QVariant", "QVariant", "QVariant")
    def add_component(
        self,
        component_type,
        name,
        description="",
        parent_index=0,
        transform_index=-1,
        geometry_model=None,
        pixel_model=None,
        transform_model=None,
    ):
        if component_type in ComponentType.values():
            dependent_transform = None
            if self.components and transform_index in range(
                0, len(self.components[parent_index - 1].transforms)
            ):
                dependent_transform = self.components[parent_index - 1].transforms[
                    transform_index
                ]
            component = Component(
                component_type=ComponentType(component_type),
                name=name,
                description=description,
                transform_parent=self.components[parent_index - 1],
                dependent_transform=dependent_transform,
                geometry=geometry_model.get_geometry(),
                pixel_data=None
                if pixel_model is None
                else pixel_model.get_pixel_model(),
                transforms=[]
                if transform_model is None
                else transform_model.transforms,
            )
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
            self.components.append(component)
            self.transform_models.append(TransformationModel(component.transforms))
            self.endInsertRows()
            self.update_removable()
            self.update_transforms_deletable()

    @Slot(int)
    def remove_component(self, index):
        if self.is_removable(index):
            self.beginRemoveRows(QModelIndex(), index, index)
            self.components.pop(index)
            self.transform_models.pop(index)
            self.endRemoveRows()
            self.update_removable()
            # If parent indexes aren't refreshed, the UI could be displaying the wrong parent
            self.dataChanged.emit(
                self.createIndex(0, 0),
                self.createIndex(self.rowCount() - 1, 0),
                InstrumentModel.TransformParentIndexRole,
            )
            self.update_transforms_deletable()

    def send_model_updated(self):
        self.model_updated.emit(self)

    def update_transforms_deletable(self):
        """
        Called by
         - the same transformsUpdated signal
         - when removing and adding components
         - or changing transform parent settings
        """
        for transform_model in self.transform_models:
            transform_model.reset_deletable()
        for component in self.components:
            if (
                component.transform_parent is not None
                and component.dependent_transform is not None
            ):
                parent_index = self.components.index(component.transform_parent)
                transform_model = self.transform_models[parent_index]
                transform_index = component.transform_parent.transforms.index(
                    component.dependent_transform
                )
                transform_model.set_deletable(transform_index, False)

        self.dataChanged.emit(
            self.createIndex(0, 0),
            self.createIndex(self.rowCount(), 0),
            [InstrumentModel.DependentTransformIndexRole],
        )

    @Slot(int)
    def transforms_updated(self, index: int):
        """
        Updates the transform matrices for components at, or dependent on, transforms at the index.
        As well as updating the de
        """
        if index in range(self.rowCount()):
            component = self.components[index]
            model_index = self.createIndex(index, 0)
            self.dataChanged.emit(
                model_index, model_index, InstrumentModel.TransformMatrixRole
            )
            self.update_child_transforms(component)

    def replace_contents(self, components):
        self.beginResetModel()
        self.components = components
        self.transform_models = [
            TransformationModel(component.transforms) for component in components
        ]
        self.update_transforms_deletable()
        self.endResetModel()

    def generate_matrix(self, component: Component):
        matrix = QMatrix4x4()

        def apply_transforms(item: Component, dependent_index: int):
            if item.transform_parent is not None and item != item.transform_parent:
                if item.dependent_transform is None:
                    index = -1
                else:
                    index = item.transform_parent.transforms.index(
                        item.dependent_transform
                    )
                apply_transforms(item.transform_parent, index)

            if dependent_index == -1:
                transforms = item.transforms
            else:
                transforms = item.transforms[: dependent_index + 1]

            for transform in transforms:
                if isinstance(transform, Translation):
                    matrix.translate(
                        transform.vector.x, transform.vector.y, transform.vector.z
                    )
                elif isinstance(transform, Rotation):
                    matrix.rotate(
                        transform.angle,
                        QVector3D(transform.axis.x, transform.axis.y, transform.axis.z),
                    )

        apply_transforms(component, -1)
        return matrix

    def update_child_transforms(self, component):
        for i in range(len(self.components)):
            candidate = self.components[i]
            if candidate.transform_parent is component and candidate is not component:
                model_index = self.createIndex(i, 0)
                self.dataChanged.emit(
                    model_index, model_index, InstrumentModel.TransformMatrixRole
                )
                self.update_child_transforms(candidate)

    @Slot(int, result="QVariant")
    def get_transform_model(self, index: int):
        return self.transform_models[index]

    @Slot(str, result=str)
    def generate_component_name(self, base):
        """Generates a unique name for a new component using a common base string"""
        return generate_unique_name(base, self.components)

    def is_removable(self, index: int):
        """
        Determine if a component can be removed from the model

        The initial sample should never be removable, and neither should transform parents of other components.
        """
        if index == 0:
            return False
        component = self.components[index]
        return (
            len(
                [
                    c
                    for c in self.components
                    if c.transform_parent is component and c is not component
                ]
            )
            == 0
        )

    def update_removable(self):
        self.dataChanged.emit(
            self.createIndex(0, 0),
            self.createIndex(len(self.components), 0),
            InstrumentModel.RemovableRole,
        )

    @Slot(int)
    def update_mesh(self, index: int):
        """
        Slot to be called when another model updates properties that require a component's mesh to be updated

        :param index: The index in this model of the component needing it's mesh updated
        """
        model_index = self.createIndex(index, 0)
        self.dataChanged.emit(model_index, model_index, InstrumentModel.MeshRole)
