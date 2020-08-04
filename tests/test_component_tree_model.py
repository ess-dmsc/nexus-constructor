from nexus_constructor.component_tree_model import (
    ComponentTreeModel,
    ComponentInfo,
    LinkTransformation,
)
from nexus_constructor.model.model import Model
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.entry import Instrument
import pytest
from PySide2.QtCore import QModelIndex, Qt
from typing import Any, Optional, List, Tuple
from PySide2.QtGui import QVector3D

from nexus_constructor.model.value_type import ValueTypes


def _add_component_to_file(
    field_name: str, field_value: Any, component_name: str = "test_component"
):
    component = Component(component_name)
    component.set_field_value(
        field_name,
        Dataset(
            name=field_name, type=ValueTypes.DOUBLE, size="[1]", values=field_value
        ),
        dtype=ValueTypes.DOUBLE,
    )

    return component


@pytest.fixture(scope="function")
def model():
    entry = Entry()
    entry.instrument = Instrument()
    model = Model(entry)
    return model


class FakeTransformationChangedSignal:
    def __init__(self):
        pass

    def emit(self):
        pass


class FakeInstrument(list):
    def __init__(self, component_list: Optional[List[Component]] = None):
        super().__init__()
        if component_list is not None:
            self.extend(component_list)
        self.name = "instrument"

    def get_component_list(self):
        return self

    def add_component(self, name: str, nx_class: str, description: str):
        return _add_component_to_file(name, 42, "component_name")


def get_component():
    return Component("test_1")


def create_component_tree_model(
    components: Optional[List[Component]] = None,
) -> Tuple[ComponentTreeModel, FakeInstrument]:
    entry = Entry()
    instrument = FakeInstrument(components)
    entry.instrument = instrument
    model = Model(entry)
    return ComponentTreeModel(model), instrument


def test_number_of_components_0():
    test_component_tree_model, _ = create_component_tree_model()
    test_index = QModelIndex()
    assert test_component_tree_model.rowCount(test_index) == 0


def test_number_of_components_1():
    test_component_tree_model, _ = create_component_tree_model([get_component()])

    test_index = QModelIndex()

    assert test_component_tree_model.rowCount(test_index) == 1


def test_number_of_components_2():
    test_component_tree_model, _ = create_component_tree_model(
        [get_component(), get_component()]
    )

    test_index = QModelIndex()

    assert test_component_tree_model.rowCount(test_index) == 2


def test_component_has_2_rows():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_index = test_component_tree_model.createIndex(0, 0, test_instrument[0])

    assert test_component_tree_model.rowCount(test_index) == 2


def test_transformation_list_has_0_rows():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_instrument[0].stored_transforms = test_instrument[0].transforms

    test_index = test_component_tree_model.createIndex(
        0, 0, test_instrument[0].stored_transforms
    )

    assert test_component_tree_model.rowCount(test_index) == 0


def test_transformation_list_has_1_rows():
    component = Component("test")
    translation = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = translation
    component.stored_transforms = component.transforms
    test_component_tree_model, _ = create_component_tree_model([component])

    test_index = test_component_tree_model.createIndex(
        0, 0, component.stored_transforms
    )

    assert test_component_tree_model.rowCount(test_index) == 1


def test_transformation_has_0_rows():
    component = Component("test")
    translation = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = translation
    component.stored_transforms = component.transforms
    test_component_tree_model, _ = create_component_tree_model([component])

    test_index = test_component_tree_model.createIndex(
        0, 0, component.stored_transforms[0]
    )

    assert test_component_tree_model.rowCount(test_index) == 0


def test_transformation_link_has_0_rows():
    component = Component("test")
    translation = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = translation
    component.stored_transforms = component.transforms
    test_component_tree_model, _ = create_component_tree_model([component])

    test_index = test_component_tree_model.createIndex(
        0, 0, component.stored_transforms[0]
    )

    assert test_component_tree_model.rowCount(test_index) == 0


def test_rowCount_gets_unknown_type():
    test_component_tree_model, _ = create_component_tree_model()

    test_index = test_component_tree_model.createIndex(0, 0, {})

    with pytest.raises(RuntimeError):
        test_component_tree_model.rowCount(test_index)


def test_get_default_parent():
    test_component_tree_model, _ = create_component_tree_model()

    test_index = QModelIndex()

    assert test_component_tree_model.parent(test_index) == QModelIndex()


def test_get_component_parent():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_index = test_component_tree_model.createIndex(0, 0, test_instrument[0])

    assert test_component_tree_model.parent(test_index) == QModelIndex()


def test_get_transform_list_parent():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_instrument[0].stored_transforms = test_instrument[0].transforms

    test_index = test_component_tree_model.createIndex(
        0, 0, test_instrument[0].stored_transforms
    )

    temp_parent = test_component_tree_model.parent(test_index)

    assert temp_parent.internalPointer() is test_instrument[0]
    assert temp_parent.row() == 0


def test_get_transform_list_parent_v2():
    zeroth_component = get_component()
    first_component = get_component()
    zeroth_component.stored_transforms = zeroth_component.transforms
    first_component.stored_transforms = first_component.transforms
    first_component.name = "Some other name"
    test_component_tree_model, _ = create_component_tree_model(
        [zeroth_component, first_component]
    )

    test_index = test_component_tree_model.createIndex(
        0, 0, first_component.stored_transforms
    )

    temp_parent = test_component_tree_model.parent(test_index)

    assert temp_parent.internalPointer() is first_component
    assert temp_parent.row() == 1


def test_get_component_info_parent():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    # Creating ComponentInfo in-line causes a segmentation error
    temp_component_info = ComponentInfo(parent=test_instrument[0])
    test_index = test_component_tree_model.createIndex(0, 0, temp_component_info)

    assert (
        test_component_tree_model.parent(test_index).internalPointer()
        is test_instrument[0]
    )


def test_get_transformation_link_parent():
    component = get_component()
    component.stored_transforms = component.transforms
    transform_link = LinkTransformation(component.stored_transforms)
    component.stored_transforms.link = transform_link
    component.stored_transforms.has_link = True

    test_component_tree_model, test_instrument = create_component_tree_model(
        [component]
    )

    test_index = test_component_tree_model.createIndex(0, 0, transform_link)

    found_parent = test_component_tree_model.parent(test_index)
    assert found_parent.internalPointer() == test_instrument[0].stored_transforms
    assert found_parent.row() == 1


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

    test_index = test_component_tree_model.createIndex(0, 0, test_instrument[0])

    assert (
        test_component_tree_model.data(test_index, Qt.DisplayRole) is test_instrument[0]
    )


def test_get_data_success_2():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_index = test_component_tree_model.createIndex(0, 0, test_instrument[0])

    assert test_component_tree_model.data(test_index, Qt.SizeHintRole) is None


def test_get_data_fail():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_component_tree_model.createIndex(0, 0, test_instrument[0])

    assert test_component_tree_model.data(QModelIndex(), Qt.DisplayRole) is None


def test_get_flags_fail():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    test_component_tree_model.createIndex(0, 0, test_instrument[0])

    assert test_component_tree_model.flags(QModelIndex()) is Qt.NoItemFlags


def test_get_flags_component():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    index = test_component_tree_model.createIndex(0, 0, test_instrument[0])

    assert test_component_tree_model.flags(index) == (
        Qt.ItemIsEnabled | Qt.ItemIsSelectable
    )


def test_get_flags_component_info():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    item = ComponentInfo(parent=test_instrument[0])
    index = test_component_tree_model.createIndex(0, 0, item)

    assert test_component_tree_model.flags(index) == Qt.ItemIsEnabled


def test_get_flags_transformation_list():
    test_component_tree_model, test_instrument = create_component_tree_model(
        [get_component()]
    )

    component = test_instrument[0]
    component.stored_transforms = component.transforms
    index = test_component_tree_model.createIndex(0, 0, component.stored_transforms)

    assert (
        test_component_tree_model.flags(index) == Qt.ItemIsEnabled | Qt.ItemIsSelectable
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
        == Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    )


def test_add_component():
    test_component_tree_model, _ = create_component_tree_model()

    assert test_component_tree_model.rowCount(QModelIndex()) == 0
    test_component_tree_model.add_component(get_component())

    assert test_component_tree_model.rowCount(QModelIndex()) == 1


def test_add_rotation():
    test_component_tree_model, _ = create_component_tree_model()

    test_component_tree_model.add_component(get_component())
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    transformation_list_index = test_component_tree_model.index(1, 0, component_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 0
    test_component_tree_model.add_rotation(component_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 1
    transform_index = test_component_tree_model.index(0, 0, transformation_list_index)
    assert transform_index.internalPointer().transform_type == "Rotation"


def test_add_translation():
    test_component_tree_model, _ = create_component_tree_model()

    test_component_tree_model.add_component(get_component())
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    transformation_list_index = test_component_tree_model.index(1, 0, component_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 0
    test_component_tree_model.add_translation(component_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 1
    transform_index = test_component_tree_model.index(0, 0, transformation_list_index)
    assert transform_index.internalPointer().transform_type == "Translation"


def test_add_transformation_alt_1():
    test_component_tree_model, _ = create_component_tree_model()

    test_component_tree_model.add_component(get_component())
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    transformation_list_index = test_component_tree_model.index(1, 0, component_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 0
    test_component_tree_model.add_translation(transformation_list_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 1


def test_add_transformation_alt_2():
    test_component_tree_model, _ = create_component_tree_model()

    test_component_tree_model.add_component(get_component())
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    transformation_list_index = test_component_tree_model.index(1, 0, component_index)
    test_component_tree_model.add_translation(transformation_list_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 1
    transform_index = test_component_tree_model.index(0, 0, transformation_list_index)
    test_component_tree_model.add_translation(transform_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 2


def test_add_link_alt_1():
    test_component_tree_model, _ = create_component_tree_model()

    test_component_tree_model.add_component(get_component())
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    transformation_list_index = test_component_tree_model.index(1, 0, component_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 0
    test_component_tree_model.add_link(component_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 1
    assert transformation_list_index.internalPointer().has_link
    assert len(transformation_list_index.internalPointer()) == 0


def test_add_link_alt_2():
    test_component_tree_model, _ = create_component_tree_model()

    test_component_tree_model.add_component(get_component())
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    transformation_list_index = test_component_tree_model.index(1, 0, component_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 0
    test_component_tree_model.add_link(transformation_list_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 1
    assert transformation_list_index.internalPointer().has_link
    assert len(transformation_list_index.internalPointer()) == 0


def test_add_link_alt_3():
    test_component_tree_model, _ = create_component_tree_model()

    test_component_tree_model.add_component(get_component())
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    transformation_list_index = test_component_tree_model.index(1, 0, component_index)
    test_component_tree_model.add_rotation(component_index)
    transform_index = test_component_tree_model.index(0, 0, transformation_list_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 1
    test_component_tree_model.add_link(transform_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 2
    assert transformation_list_index.internalPointer().has_link
    assert len(transformation_list_index.internalPointer()) == 1


def test_add_link_multiple_times():
    test_component_tree_model, _ = create_component_tree_model()

    test_component_tree_model.add_component(get_component())
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    transformation_list_index = test_component_tree_model.index(1, 0, component_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 0
    test_component_tree_model.add_link(component_index)
    first_link = transformation_list_index.internalPointer().link
    test_component_tree_model.add_link(component_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 1
    assert transformation_list_index.internalPointer().has_link
    assert len(transformation_list_index.internalPointer()) == 0
    assert first_link is transformation_list_index.internalPointer().link


def test_remove_component(model):
    test_component_tree_model = ComponentTreeModel(model)
    model.entry.instrument.add_component(Component(name="Some name"))
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    assert test_component_tree_model.rowCount(QModelIndex()) == 1
    test_component_tree_model.remove_node(component_index)
    assert test_component_tree_model.rowCount(QModelIndex()) == 0


def test_remove_component_with_transformation(model):
    test_component_tree_model = ComponentTreeModel(model)
    model.entry.instrument.add_component(Component(name="Some name"))
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    test_component_tree_model.add_rotation(component_index)
    assert test_component_tree_model.rowCount(QModelIndex()) == 1
    test_component_tree_model.remove_node(component_index)
    assert test_component_tree_model.rowCount(QModelIndex()) == 0, (
        "Expected component to be successfully deleted because it has "
        "a transformation that only has it as a dependent"
    )


def test_remove_transformation(model):

    test_component_tree_model = ComponentTreeModel(model)
    model.entry.instrument.add_component(Component(name="Some name"))
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    test_component_tree_model.add_rotation(component_index)
    transformation_list_index = test_component_tree_model.index(1, 0, component_index)
    transformation_index = test_component_tree_model.index(
        0, 0, transformation_list_index
    )
    assert test_component_tree_model.rowCount(transformation_list_index) == 1
    test_component_tree_model.remove_node(transformation_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 0


def test_remove_link(model):
    test_component_tree_model = ComponentTreeModel(model)
    model.entry.instrument.add_component(Component(name="Some name"))
    component_index = test_component_tree_model.index(0, 0, QModelIndex())
    test_component_tree_model.add_link(component_index)
    transformation_list_index = test_component_tree_model.index(1, 0, component_index)
    transformation_index = test_component_tree_model.index(
        0, 0, transformation_list_index
    )
    assert test_component_tree_model.rowCount(transformation_list_index) == 1
    assert len(transformation_list_index.internalPointer()) == 0
    test_component_tree_model.remove_node(transformation_index)
    assert test_component_tree_model.rowCount(transformation_list_index) == 0
