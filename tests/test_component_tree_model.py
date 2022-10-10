from typing import Any, List, Optional, Tuple

import pytest
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QVector3D

from nexus_constructor.common_attrs import NX_TRANSFORMATIONS
from nexus_constructor.component_tree_model import ComponentInfo
from nexus_constructor.component_tree_model import NexusTreeModel as ComponentTreeModel
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.group import Group
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import Dataset
from nexus_constructor.model.value_type import ValueTypes


def _add_component_to_file(
    field_name: str, field_value: Any, component_name: str = "test_component"
):
    component = Component(component_name)
    component.set_field_value(
        field_name,
        Dataset(
            parent_node=None,
            name=field_name,
            type=ValueTypes.DOUBLE,
            size="[1]",
            values=field_value,
        ),
        dtype=ValueTypes.DOUBLE,
    )

    return component


@pytest.fixture(scope="function")
def model():
    model = Model()
    return model


def get_component():
    component = Component("test_1")
    component.nx_class = "NXslit"
    return component


def create_component_tree_model(
    components: Optional[List[Component]] = None,
) -> Tuple[ComponentTreeModel, Entry]:
    model = Model()
    if components is not None:
        for component in components:
            model.entry.children.append(component)
            model.append_component(component)
            component.parent_node = model.entry
    component_model = ComponentTreeModel(model)

    return component_model, model.entry


def test_number_of_groups_0():
    test_component_tree_model, _ = create_component_tree_model()
    test_index = test_component_tree_model.index(0, 0, QModelIndex())
    assert test_component_tree_model.rowCount(test_index) == 0


def test_number_of_groups_1():
    test_component_tree_model, _ = create_component_tree_model([get_component()])
    test_index = test_component_tree_model.index(0, 0, QModelIndex())
    assert test_component_tree_model.rowCount(test_index) == 1


def test_number_of_groups_2():
    test_component_tree_model, _ = create_component_tree_model(
        [get_component(), get_component()]
    )
    test_index = test_component_tree_model.index(0, 0, QModelIndex())

    assert test_component_tree_model.rowCount(test_index) == 2


def test_component_has_0_rows():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_index = test_component_tree_model.createIndex(
        0, 0, test_instrument.children[0]
    )

    assert test_component_tree_model.rowCount(test_index) == 0


def test_transformation_list_has_0_rows():
    component = get_component()
    translation = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = translation
    component.stored_transforms = component.transforms
    test_component_tree_model, _ = create_component_tree_model([component])

    test_index = test_component_tree_model.createIndex(
        0, 0, component.stored_transforms
    )

    assert test_component_tree_model.rowCount(test_index) == 0


def test_transformation_has_0_rows():
    component = get_component()
    translation = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = translation
    component.stored_transforms = component.transforms
    test_component_tree_model, _ = create_component_tree_model([component])

    test_index = test_component_tree_model.createIndex(
        0, 0, component.stored_transforms[0]
    )

    assert test_component_tree_model.rowCount(test_index) == 0


def test_transformation_link_has_0_rows():
    component = get_component()
    translation = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = translation
    component.stored_transforms = component.transforms
    test_component_tree_model, _ = create_component_tree_model([component])

    test_index = test_component_tree_model.createIndex(
        0, 0, component.stored_transforms[0]
    )

    assert test_component_tree_model.rowCount(test_index) == 0


def test_get_default_parent():
    test_component_tree_model, _ = create_component_tree_model()

    test_index = QModelIndex()

    assert test_component_tree_model.parent(test_index) == QModelIndex()


def test_get_invalid_index():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_index = QModelIndex()

    assert test_component_tree_model.index(2, 0, test_index) == QModelIndex()


def test_get_data_success_1():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_index = test_component_tree_model.createIndex(
        0, 0, test_instrument.children[0]
    )

    assert (
        test_component_tree_model.data(test_index, Qt.DisplayRole)
        is test_instrument.children[0]
    )


def test_get_data_success_2():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_index = test_component_tree_model.createIndex(
        0, 0, test_instrument.children[0]
    )

    assert test_component_tree_model.data(test_index, Qt.SizeHintRole) is None


def test_get_data_fail():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_component_tree_model.createIndex(0, 0, test_instrument.children[0])

    assert test_component_tree_model.data(QModelIndex(), Qt.DisplayRole) is None


def test_get_flags_fail():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_component_tree_model.createIndex(0, 0, test_instrument.children[0])

    assert test_component_tree_model.flags(QModelIndex()) is Qt.NoItemFlags


def test_get_flags_component():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    index = test_component_tree_model.createIndex(0, 0, test_instrument.children[0])

    assert test_component_tree_model.flags(index) == (
        Qt.ItemIsEnabled
        | Qt.ItemIsSelectable
        | Qt.ItemIsDropEnabled
        | Qt.ItemIsDragEnabled
    )


def test_get_flags_component_info():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    item = ComponentInfo(parent=test_instrument.children[0])
    index = test_component_tree_model.createIndex(0, 0, item)

    assert (
        test_component_tree_model.flags(index)
        == Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled
    )


def test_get_flags_transformation_list():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    transformation_group = Group(name="transformations")
    transformation_group.nx_class = NX_TRANSFORMATIONS
    index = test_component_tree_model.createIndex(0, 0, transformation_group)

    assert (
        test_component_tree_model.flags(index)
        == Qt.ItemIsEnabled
        | Qt.ItemIsSelectable
        | Qt.ItemIsDragEnabled
        | Qt.ItemIsDropEnabled
    )


def test_get_flags_other():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    class TestObject:
        pass

    test_item = TestObject()
    index = test_component_tree_model.createIndex(0, 0, test_item)

    assert (
        test_component_tree_model.flags(index)
        == Qt.ItemIsEnabled
        | Qt.ItemIsSelectable
        | Qt.ItemIsEditable
        | Qt.ItemIsDropEnabled
        | Qt.ItemIsDragEnabled
    )


def test_add_group():
    test_component_tree_model, _ = create_component_tree_model()
    assert test_component_tree_model.rowCount(QModelIndex()) == 1
    test_component_tree_model.add_group(get_component())
    index = test_component_tree_model.index(0, 0, QModelIndex())
    assert test_component_tree_model.rowCount(index) == 1
