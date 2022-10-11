import pickle
from json import loads
from typing import Dict, List, Optional, Tuple, Union

import PySide6.QtGui
from PySide6.QtCore import QAbstractItemModel, QByteArray, QMimeData, QModelIndex, Qt
from PySide6.QtGui import QVector3D
from PySide6.QtWidgets import QMessageBox

from nexus_constructor.common_attrs import (
    NX_TRANSFORMATIONS,
    TRANSFORMATIONS,
    TransformationType,
)
from nexus_constructor.link_transformation import LinkTransformation
from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import (
    Dataset,
    FileWriterModule,
    create_fw_module_object,
)
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.model.value_type import ValueTypes
from nexus_constructor.transformations_list import TransformationsList
from nexus_constructor.unique_name import generate_unique_name


class ComponentInfo(object):
    def __init__(self, parent: Component):
        super().__init__()
        self.parent = parent


class NexusTreeModel(QAbstractItemModel):
    def __init__(self, model: Model, parent=None):
        super().__init__(parent)
        self.model = model
        self.tree_root = self.model.entry
        self.current_nxs_obj: Optional[
            Tuple[Union[Group, FileWriterModule], QModelIndex]
        ] = (self.model.entry, None)
        self.path_translation_dict: Dict[str, str] = {}

    def replace_model(self, model):
        self.model = model

    def find_index_of_group(self, group: Group) -> QModelIndex:
        abs_path = group.absolute_path.split("/")[2:]
        sub_tree_root = self.model.entry
        for item in abs_path:
            sub_tree_root = sub_tree_root[item]
        if not sub_tree_root or not sub_tree_root.parent_node:
            return self.createIndex(0, 0, self.model.entry)
        return self.index_from_component(sub_tree_root)

    def columnCount(self, parent: QModelIndex) -> int:
        return 1

    def find_component_of(self, index: QModelIndex):
        if index.isValid():
            item = index.internalPointer()
            if isinstance(item, Component):
                return index
            parent_item = item.parent_node
            if parent_item:
                parent_index = self.createIndex(parent_item.row(), 0, parent_item)
                next_index = self.find_component_of(parent_index)
                if isinstance(next_index.internalPointer(), Component):
                    return next_index
            if item:
                if item.name == item.absolute_path.split("/")[1]:
                    return self.createIndex(0, 0, item)
        return QModelIndex()

    def parent(self, index: QModelIndex):
        if index.isValid():
            parent_item = index.internalPointer().parent_node
            if parent_item:
                return self.createIndex(parent_item.row(), 0, parent_item)
        return QModelIndex()

    def data(self, index: QModelIndex, role: Qt.DisplayRole):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item
        elif role == Qt.SizeHintRole:
            return

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            return self.createIndex(row, column, self.tree_root)
        parent_item = parent.internalPointer()
        index = self.createIndex(row, column, parent_item.children[row])
        return index

    def index_from_component(self, component: Group):
        row = component.parent_node.children.index(component)
        return self.createIndex(row, 0, component)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        parent_item = index.internalPointer()
        self.current_nxs_obj = (parent_item, index)
        if (
            isinstance(parent_item, Group)
            and parent_item.nx_class == NX_TRANSFORMATIONS
        ):
            return (
                Qt.ItemIsEnabled
                | Qt.ItemIsSelectable
                | Qt.ItemIsDragEnabled
                | Qt.ItemIsDropEnabled
            )
        elif isinstance(parent_item, Component):
            return (
                Qt.ItemIsEnabled
                | Qt.ItemIsSelectable
                | Qt.ItemIsDropEnabled
                | Qt.ItemIsDragEnabled
            )
        elif isinstance(parent_item, ComponentInfo):
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
        elif isinstance(parent_item, Transformation):
            return (
                Qt.ItemIsSelectable
                | Qt.ItemIsEnabled
                | Qt.ItemIsEditable
                | Qt.ItemIsDropEnabled
                | Qt.ItemIsDragEnabled
            )
        elif isinstance(parent_item, (FileWriterModule, LinkTransformation)):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return (
            Qt.ItemIsSelectable
            | Qt.ItemIsEnabled
            | Qt.ItemIsEditable
            | Qt.ItemIsDropEnabled
            | Qt.ItemIsDragEnabled
        )

    def mimeTypes(self):
        return [
            "streaming/writer_module",
            "moving/group",
            "node/transformation",
        ]

    def supportedDropActions(self) -> PySide6.QtCore.Qt.DropActions:
        return Qt.DropAction.MoveAction | Qt.DropAction.CopyAction

    def mimeData(self, indexes):
        index = indexes[0]
        mimedata = QMimeData()
        data = QByteArray(pickle.dumps(index.internalPointer()))
        if isinstance(index.internalPointer(), Transformation):
            mimedata.setData("node/transformation", data)
        else:
            mimedata.setData("moving/group", data)
        self._stored_index = index
        return mimedata

    def canDropMimeData(self, mimedata, action, row, column, parentIndex):
        drag_item = self._stored_index.internalPointer()
        drop_item = parentIndex.internalPointer()
        if mimedata.hasFormat("node/transformation"):
            if isinstance(drop_item, Transformation):
                if drop_item.parent_component.stored_transforms.has_link:  # type: ignore
                    return False
                return True
            else:
                return False
        elif isinstance(drag_item, Group) and drag_item.nx_class == NX_TRANSFORMATIONS:
            return False
        if drag_item == drop_item and row == -1:
            return False
        if isinstance(drag_item, Group):
            if drop_item and drag_item.absolute_path in drop_item.absolute_path:
                return False
            if (
                isinstance(drop_item, Component)
                and drop_item
                and not drop_item.group_placeholder
            ):
                return True
            elif (
                isinstance(drop_item, Group)
                and drop_item
                and not drop_item.group_placeholder
            ):
                return True
            else:
                return False
        return False

    def update_all_absolute_paths(self, parentIndex):
        node = parentIndex.internalPointer()
        while node.parent_node is not None:
            node = node.parent_node
        self.recursive_path_updater(node)

    def recursive_path_updater(self, node):
        for child in node.children:
            if isinstance(child, Group):
                _ = child.absolute_path
                self.recursive_path_updater(child)
            else:
                try:
                    _ = child.absolute_path
                except Exception:
                    pass

    def recursive_path_namer(self, node, old_prefix, new_prefix):
        for child in node.children:
            if isinstance(child, Group):
                name = child.name
                old_absolute_path = old_prefix + "/" + name
                new_absolute_path = new_prefix + "/" + name
                self.path_translation_dict[new_absolute_path] = old_absolute_path
                self.model.signals.path_name_changed.emit(
                    old_absolute_path, new_absolute_path
                )
                self.recursive_path_namer(child, old_absolute_path, new_absolute_path)

    def create_path_translation_dict(self, drag_child_item, drop_item):
        self.path_translation_dict = {}
        drag_child_name = drag_child_item.absolute_path
        old_prefix = drag_child_name
        new_prefix = drop_item.absolute_path + "/" + drag_child_item.name
        self.recursive_path_namer(drag_child_item, old_prefix, new_prefix)

    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        if mimedata.hasFormat("moving/group"):
            drag_child_index = self._stored_index
            drag_child_item = self._stored_index.internalPointer()
            drag_child_name = drag_child_item.absolute_path
            drop_index = parentIndex
            drop_item = parentIndex.internalPointer()
            drop_item_name = drop_item.absolute_path
            drop_between = True
            if row == -1:
                drop_between = False

            self.create_path_translation_dict(drag_child_item, drop_item)
            drag_parent = self.parent(drag_child_index)
            remove_index = self._get_row_of_child(drag_child_item)
            self.beginRemoveRows(drag_parent, remove_index, remove_index)
            drag_group_parent: Group = drag_parent.internalPointer()
            children = drag_group_parent.children
            children.pop(remove_index)
            self.endRemoveRows()

            drop_parent = drop_index
            group_parent: Group = drop_parent.internalPointer()  # type: ignore
            children = group_parent.children
            if drop_between:
                print(
                    "Dropping {} between {} and {} in group {}".format(
                        drag_child_name, row, row + 1, drop_item_name
                    )
                )
                self.beginInsertRows(drop_parent, row, row)
                children.insert(row, drag_child_item)
                self.endInsertRows()
            else:
                print(
                    "Dropping {} inside the group {}".format(
                        drag_child_name, drop_item_name
                    )
                )
                insert_location = len(drop_parent.data().children)
                self.beginInsertRows(drop_parent, insert_location, insert_location)
                children.insert(insert_location, drag_child_item)
                self.endInsertRows()

            drag_child_item.parent_node = drop_parent.internalPointer()
            new_absolute_path = drag_child_item.absolute_path
            self.update_all_absolute_paths(drop_index)
            self.model.signals.path_name_changed.emit(
                drag_child_name, new_absolute_path
            )
            self.model.signals.group_edited.emit(drop_parent, True)
        elif mimedata.hasFormat("node/transformation"):
            selected_child_item = pickle.loads(mimedata.data("node/transformation"))
            selected_child_index = self._stored_index

            component_index = self.parent(parentIndex)

            # Remove the selected transformation and its writer module
            remove_transform = selected_child_index.internalPointer()
            transformation_list = remove_transform.parent_component.stored_transforms
            transformation_list_index = self.parent(selected_child_index)
            remove_pos = transformation_list.index(remove_transform)
            self.beginRemoveRows(transformation_list_index, remove_pos, remove_pos)
            transformation_list.pop(remove_pos)
            self.endRemoveRows()
            self.model.signals.transformation_changed.emit()

            parent = self.parent(selected_child_index)
            remove_index = self._get_row_of_child(selected_child_item)
            self.beginRemoveRows(parent, remove_index, remove_index)
            group_parent: Group = parent.internalPointer()  # type: ignore
            children = group_parent.children
            children.pop(remove_index)
            self.endRemoveRows()

            insert_location = parentIndex.row()

            # Insert the selected transformation and its writer module
            self.beginInsertRows(selected_child_index, insert_location, insert_location)
            transformation_list.insert(
                insert_location, selected_child_index.internalPointer()
            )
            self.endInsertRows()

            self.beginInsertRows(parent, insert_location, insert_location)
            children = group_parent.children
            children.insert(insert_location, selected_child_index.internalPointer())
            self.endInsertRows()

            # Force link to the bottom   Needs to be further investigated.
            # Maybe dont allow dragNdrop when you have a link?
            if transformation_list.has_link:
                group = transformation_list[-1].parent_node
                for i, child in enumerate(group.children):
                    if not isinstance(child, Transformation):
                        link_idx = i
                group.children[link_idx], group.children[i] = (
                    group.children[i],
                    group.children[link_idx],
                )

            # Reorganize depends.
            for i, t in enumerate(transformation_list):
                if i == 0:
                    t.remove_from_dependee_chain()
                    t.register_dependent(component_index.internalPointer().parent_node)
                    t.depends_on = transformation_list[i + 1]
                    transformation_list[0].parent_component.depends_on = t
                elif i < len(transformation_list) - 1:
                    t.depends_on = transformation_list[i + 1]
                    t.deregister_dependent(
                        component_index.internalPointer().parent_node
                    )
                    t.register_dependent(transformation_list[i - 1])
            transformation_list[-1].depends_on = None
            self.model.signals.transformation_changed.emit()
            self.model.signals.group_edited.emit(component_index, True)
            return True
        elif mimedata.hasFormat("streaming/writer_module"):
            module_config = loads(mimedata.text())
            insert_location = len(parentIndex.data().children)
            if row != -1:
                insert_location = row
            new_module = create_fw_module_object(
                module_config["module"], module_config["config"], parentIndex.data()
            )
            self.beginInsertRows(QModelIndex(), insert_location, insert_location)
            parentIndex.data().children.insert(insert_location, new_module)
            self.endInsertRows()
        return True

    def rowCount(self, parent: QModelIndex) -> int:
        if not parent.isValid():
            return 1
        else:
            node = parent.internalPointer()
            if isinstance(node, Group):
                return node.number_of_children()
            else:
                return 0

    def add_group(self, new_group: Group):
        parent_node, _ = self.current_nxs_obj
        if not isinstance(parent_node, Group):
            parent_node = parent_node.parent_node
        pointer = self.createIndex(parent_node.number_of_children(), 0, parent_node)
        self.beginInsertRows(
            pointer, parent_node.number_of_children(), parent_node.number_of_children()
        )
        if isinstance(new_group, Component):
            self.model.append_component(new_group)
        parent_node[new_group.name] = new_group
        self.endInsertRows()

    @staticmethod
    def _get_row_of_child(row_child):
        if not row_child.parent_node:
            return -1
        for c, child in enumerate(row_child.parent_node.children):
            if row_child == child:
                return c
        return -1

    def headerData(self, section, orientation, role):
        return None

    def add_link(self, node: QModelIndex):
        parent_item = node.internalPointer()

        target_index, transformation_list, component = self._get_transformation_list(
            node, parent_item
        )
        if transformation_list.has_link:
            return

        _, group = self._get_transformation_group(component)
        target_pos = len(transformation_list)
        self.beginInsertRows(target_index, target_pos, target_pos)
        group.children.append(transformation_list.link)
        transformation_list.link.parent_node = group
        transformation_list.has_link = True
        self.endInsertRows()

    def add_transformation(self, parent_index: QModelIndex, transformation_type: str):
        parent_item = parent_index.internalPointer()
        transformation_list = None
        parent_component = None
        target_pos = 0
        target_index = QModelIndex()
        (
            parent_component,
            target_index,
            target_pos,
            transformation_list,
            component_index,
        ) = self._get_target_position(
            parent_component,
            parent_index,
            parent_item,
            target_index,
            target_pos,
            transformation_list,
        )
        new_transformation = self._create_new_transformation(
            parent_component, transformation_list, transformation_type, target_pos
        )
        new_transformation.parent_component = parent_component
        self.model.signals.group_edited.emit(component_index, False)

        self.beginInsertRows(
            target_index,
            target_pos,
            target_pos,
        )
        transformation_list.insert(target_pos, new_transformation)
        if transformation_list.has_link and not isinstance(parent_item, Transformation):
            _, group = self._get_transformation_group(parent_component)
            # Link should be last element of children list in NXtransformations
            group.children[-2], group.children[-1] = (
                group.children[-1],
                group.children[-2],
            )
        self.endInsertRows()

        parent_component.depends_on = transformation_list[0]
        linked_component = None
        if transformation_list.has_link:
            linked_component = transformation_list.link.linked_component
        for i in range(len(transformation_list) - 1):
            transformation_list[i].depends_on = transformation_list[i + 1]
        if transformation_list.has_link:
            transformation_list.link.linked_component = linked_component
            if linked_component is not None:
                transformation_list[
                    -1
                ].depends_on = transformation_list.link.linked_component.transforms[0]
        self.model.signals.transformation_changed.emit()
        self.model.signals.group_edited.emit(component_index, True)

    def add_translation(self, parent_index: QModelIndex):
        self.add_transformation(parent_index, TransformationType.TRANSLATION)

    def add_rotation(self, parent_index: QModelIndex):
        self.add_transformation(parent_index, TransformationType.ROTATION)

    @staticmethod
    def _get_transformation_group(component):
        for idx, child in enumerate(component.children):
            if isinstance(child, Group) and child.nx_class == NX_TRANSFORMATIONS:
                return idx, child
        return -1, None

    def _get_target_position(
        self,
        parent_component,
        parent_index,
        parent_item,
        target_index,
        target_pos,
        transformation_list,
    ):
        """
        :param parent_component: component to add transformation to
        :param parent_index: index of the parent_item
        :param parent_item: the component, transformation list or transformation that was selected "add" button pressed
        :param target_index: index of parent component of new transformation
        :param target_pos: position for new transformation in transformation list
        :param transformation_list: transformation list of parent_component
        """
        if isinstance(parent_item, Component):
            if parent_item.stored_transforms is None:
                parent_item.stored_transforms = parent_item.transforms
            transformation_list = parent_item.stored_transforms
            parent_component = parent_item
            target_pos = len(transformation_list) + 1
            idx, group = self._get_transformation_group(parent_component)
            target_index = self.index(idx + 1, 0, parent_index)
            component_index = parent_index
        elif (
            isinstance(parent_item, Group)
            and parent_item.nx_class == NX_TRANSFORMATIONS
        ):
            parent_component = parent_item.parent_node
            if parent_component.stored_transforms is None:
                parent_component.stored_transforms = parent_component.transforms
            transformation_list = parent_component.stored_transforms
            target_pos = len(transformation_list) + 1
            component_index = self.parent(parent_index)
            idx, _ = self._get_transformation_group(parent_component)
            target_index = self.index(idx + 1, 0, component_index)
        elif isinstance(parent_item, Transformation):
            parent_component = parent_item.parent_component
            if parent_component.stored_transforms is None:
                parent_component.stored_transforms = parent_component.transforms
            transformation_list = parent_component.stored_transforms
            target_pos = transformation_list.index(parent_item) + 1
            target_index = self.parent(parent_index)
            component_index = self.parent(target_index)
        return (
            parent_component,
            target_index,
            target_pos,
            transformation_list,
            component_index,
        )

    def _get_transformation_list(self, node, parent_item):
        transformation_list = None
        target_index = QModelIndex()
        if isinstance(parent_item, Component):
            transformation_list = parent_item.transforms
            target_index = self.index(parent_item.number_of_children(), 0, node)
            component = parent_item
        elif isinstance(parent_item, Group):
            transformation_list = parent_item.parent_node.transforms  # type: ignore
            target_index = node
            component = parent_item.parent_node  # type: ignore
        elif isinstance(parent_item, Transformation):
            transformation_list = parent_item.parent_component.transforms
            target_index = self.parent(node)
            component = parent_item.parent_component
        return target_index, transformation_list, component

    @staticmethod
    def _create_new_transformation(
        parent_component, transformation_list, transformation_type, target_pos
    ):
        values = Dataset(
            parent_node=parent_component, name="", type=ValueTypes.DOUBLE, values="0.0"
        )
        if transformation_type == TransformationType.TRANSLATION:
            new_transformation = parent_component.add_translation(
                name=generate_unique_name(
                    TransformationType.TRANSLATION, transformation_list
                ),
                vector=QVector3D(0, 0, 1.0),  # default to beam direction
                values=values,
                target_pos=target_pos,
            )
        elif transformation_type == TransformationType.ROTATION:
            new_transformation = parent_component.add_rotation(
                name=generate_unique_name(
                    TransformationType.ROTATION, transformation_list
                ),
                axis=QVector3D(1.0, 0, 0),
                angle=0.0,
                values=values,
                target_pos=target_pos,
            )
        else:
            raise ValueError(f"Unknown transformation type: {transformation_type}")
        return new_transformation

    def remove_node(self, node: QModelIndex):
        nexus_object = node.internalPointer()
        if isinstance(nexus_object, Transformation):
            self._remove_transformation(node)
        if isinstance(nexus_object, Group):
            if nexus_object.name == TRANSFORMATIONS:
                for transform in nexus_object.parent_node.transforms:  # type: ignore
                    transform.remove_from_dependee_chain()
                nexus_object.parent_node.stored_transforms = None  # type: ignore
                self.model.signals.transformation_changed.emit()
            self._remove_component(node)
        elif isinstance(nexus_object, LinkTransformation):
            self._remove_link(node)
        elif isinstance(nexus_object, FileWriterModule):
            self._remove_fw_module(node, nexus_object)

    def _remove_fw_module(self, node, module):
        parent = self.parent(node)
        remove_index = self._get_row_of_child(module)
        self.beginRemoveRows(parent, remove_index, remove_index)
        group_parent: Group = parent.internalPointer()
        children = group_parent.children
        if children:
            group_parent.add_stream_module(module.writer_module)
            children.pop(remove_index)
            del module
        self.endRemoveRows()

    def _remove_component(self, index: QModelIndex):
        component = index.internalPointer()
        transforms = []  # type: ignore
        if isinstance(component, Component):
            transforms = component.transforms
        if transforms:
            has_dependents_other_than_the_component_being_deleted = (
                len(transforms[0].dependents) > 1
            )
            if has_dependents_other_than_the_component_being_deleted:
                reply = QMessageBox.question(
                    None,
                    "Delete component?",
                    "this component has transformations that are depended on. Are you sure you want to delete it?",
                    QMessageBox.Yes,
                    QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    pass
                elif reply == QMessageBox.No:
                    return
        parent_index = QModelIndex()
        if index.internalPointer().parent_node:
            row = index.internalPointer().parent_node.row()
            if not row < 0:
                parent_index = self.createIndex(
                    row, 0, index.internalPointer().parent_node
                )
        remove_index = component.row()
        self.beginRemoveRows(parent_index, remove_index, remove_index)
        removed_components_in_group: List[str] = []
        for transform in transforms:
            transform.remove_from_dependee_chain()
        if isinstance(component, Component) and component.name in [
            c.name for c in self.model.get_components()
        ]:
            self.model.remove_component(component)
        else:
            self._remove_child_components(component, removed_components_in_group)
        component.parent_node.children.pop(component.row())
        self.endRemoveRows()
        if component.name != TRANSFORMATIONS and isinstance(component, Component):
            self.model.signals.component_removed.emit(component.absolute_path)
        elif removed_components_in_group:
            for c_name in removed_components_in_group:
                self.model.signals.component_removed.emit(c_name)

    def _remove_child_components(self, group: Group, removed_components: List[str]):
        for child in group.children:
            if isinstance(child, Component):
                removed_components.append(child.absolute_path)
                self.model.remove_component(child)
            elif isinstance(child, Group):
                self._remove_child_components(child, removed_components)

    def _remove_transformation(self, index: QModelIndex):
        remove_transform = index.internalPointer()
        if remove_transform.parent_component.stored_transforms is None:
            remove_transform.parent_component.stored_transforms = (
                remove_transform.parent_component.transforms
            )
        transformation_list = remove_transform.parent_component.stored_transforms
        transformation_list_index = self.parent(index)
        remove_pos = transformation_list.index(remove_transform)
        remove_transform.remove_from_dependee_chain()
        self.__update_link_rows()
        self.beginRemoveRows(transformation_list_index, remove_pos, remove_pos)
        transformation_list.pop(remove_pos)
        self.endRemoveRows()
        self.model.signals.transformation_changed.emit()

    def _remove_link(self, index: QModelIndex):
        link = index.internalPointer()
        transformation_list = link.parent
        transformation_list_index = self.parent(index)
        parent_group = link.parent_node
        remove_pos = len(transformation_list)
        self.beginRemoveRows(transformation_list_index, remove_pos, remove_pos)
        parent_group.children.remove(link)
        transformation_list.has_link = False
        self.endRemoveRows()
        # Update depends on
        if len(transformation_list) > 0:
            parent_transform = transformation_list[len(transformation_list) - 1]
            parent_transform.depends_on = None
        self.model.signals.transformation_changed.emit()

    def __update_link_rows(
        self,
    ):  # TODO: this function is a bit shaky and needs an update in a future PR.
        try:
            component = self.current_nxs_obj[0].parent_component  # type: ignore
            if not isinstance(component, Component):
                component = self.current_nxs_obj[0].parent_component  # type: ignore
        except AttributeError:
            print("Not able to update link rows.")
            return
        nr_of_children = component.parent_node.number_of_children()
        for i in range(nr_of_children):
            component_index = self.index(i, 0, QModelIndex())
            transformations_index = self.index(1, 0, component_index)
            transformations = transformations_index.internalPointer()
            if (
                transformations
                and isinstance(transformations, TransformationsList)
                and transformations.has_link
            ):
                transformation_rows = self.rowCount(transformations_index)
                link_index = self.index(
                    transformation_rows - 1, 0, transformations_index
                )
                self.dataChanged.emit(link_index, link_index)
