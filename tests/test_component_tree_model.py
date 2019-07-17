from nexus_constructor.component_tree_model import (
    ComponentTreeModel,
    ComponentInfo,
    LinkTransformation,
)
from nexus_constructor.component import Component
from nexus_constructor.instrument import Instrument
import pytest
from PySide2.QtCore import QModelIndex, Qt
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from typing import Any
from uuid import uuid1
from PySide2.QtGui import QVector3D


def _add_component_to_file(
    nexus_wrapper: NexusWrapper,
    field_name: str,
    field_value: Any,
    component_name: str = "test_component",
):
    component_group = nexus_wrapper.nexus_file.create_group(component_name)
    component_group.create_dataset(field_name, data=field_value)
    return component_group


class FakeInstrument(list):
    def __init__(self, component_list=[]):
        super().__init__()
        for current in component_list:
            self.append(current)

    def get_component_list(self):
        return self

    def add_component(self, name: str, nx_class: str, description: str):
        nexus_wrapper = NexusWrapper(str(uuid1()))
        component_group = _add_component_to_file(
            nexus_wrapper, name, 42, "component_name"
        )
        return Component(nexus_wrapper, component_group)


def get_component():
    nexus_wrapper = NexusWrapper(str(uuid1()))
    component_group = _add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    return Component(nexus_wrapper, component_group)


def test_number_of_components_0():
    data_under_test = FakeInstrument()
    under_test = ComponentTreeModel(data_under_test)
    test_index = QModelIndex()
    assert under_test.rowCount(test_index) == 0


def test_number_of_components_1():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    test_index = QModelIndex()

    assert under_test.rowCount(test_index) == 1


def test_number_of_components_2():
    data_under_test = FakeInstrument([get_component(), get_component()])
    under_test = ComponentTreeModel(data_under_test)

    test_index = QModelIndex()

    assert under_test.rowCount(test_index) == 2


def test_component_has_2_rows():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, data_under_test[0])

    assert under_test.rowCount(test_index) == 2


def test_transformation_list_has_0_rows():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    data_under_test[0].stored_transforms = data_under_test[0].transforms

    test_index = under_test.createIndex(0, 0, data_under_test[0].stored_transforms)

    assert under_test.rowCount(test_index) == 0


def test_transformation_list_has_1_rows():
    component = get_component()
    translation = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = translation
    data_under_test = FakeInstrument([component])
    component.stored_transforms = component.transforms
    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, component.stored_transforms)

    assert under_test.rowCount(test_index) == 1


def test_transformation_has_0_rows():
    component = get_component()
    translation = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = translation
    data_under_test = FakeInstrument([component])
    component.stored_transforms = component.transforms
    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, component.stored_transforms[0])

    assert under_test.rowCount(test_index) == 0


def test_transformation_link_has_0_rows():
    component = get_component()
    translation = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = translation
    data_under_test = FakeInstrument([component])
    component.stored_transforms = component.transforms
    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, component.stored_transforms[0])

    assert under_test.rowCount(test_index) == 0


def test_rowCount_gets_unknown_type():
    data_under_test = FakeInstrument()
    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, {})

    with pytest.raises(RuntimeError):
        under_test.rowCount(test_index)


def test_get_default_parent():
    data_under_test = FakeInstrument()
    under_test = ComponentTreeModel(data_under_test)

    test_index = QModelIndex()

    assert under_test.parent(test_index) == QModelIndex()


def test_get_component_parent():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, data_under_test[0])

    assert under_test.parent(test_index) == QModelIndex()


def test_get_transform_list_parent():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    data_under_test[0].stored_transforms = data_under_test[0].transforms

    test_index = under_test.createIndex(0, 0, data_under_test[0].stored_transforms)

    temp_parent = under_test.parent(test_index)

    assert temp_parent.internalPointer() is data_under_test[0]
    assert temp_parent.row() == 0


def test_get_transform_list_parent_v2():
    data_under_test = FakeInstrument([get_component(), get_component()])
    data_under_test[0].stored_transforms = data_under_test[0].transforms
    data_under_test[1].stored_transforms = data_under_test[1].transforms
    data_under_test[1].name = "Some other name"
    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, data_under_test[1].stored_transforms)

    temp_parent = under_test.parent(test_index)

    assert temp_parent.internalPointer() is data_under_test[1]
    assert temp_parent.row() == 1


def test_get_component_info_parent():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    # Creating ComponentInfo in-line causes a segmentation error
    temp_component_info = ComponentInfo(parent=data_under_test[0])
    test_index = under_test.createIndex(0, 0, temp_component_info)

    assert under_test.parent(test_index).internalPointer() is data_under_test[0]


def test_get_transformation_parent():
    component = get_component()
    translation = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = translation
    data_under_test = FakeInstrument([component])
    component.stored_transforms = component.transforms
    translation.parent = component.stored_transforms

    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, translation)

    found_parent = under_test.parent(test_index)
    assert found_parent.internalPointer() == data_under_test[0].stored_transforms
    assert found_parent.row() == 1


def test_get_transformation_link_parent():
    component = get_component()
    data_under_test = FakeInstrument([component])
    component.stored_transforms = component.transforms
    transform_link = LinkTransformation(component.stored_transforms)
    component.stored_transforms.link = transform_link
    component.stored_transforms.has_link = True

    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, transform_link)

    found_parent = under_test.parent(test_index)
    assert found_parent.internalPointer() == data_under_test[0].stored_transforms
    assert found_parent.row() == 1


def test_get_invalid_index():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    test_index = QModelIndex()

    assert under_test.index(2, 0, test_index) == QModelIndex()


def test_get_data_success_1():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, data_under_test[0])

    assert under_test.data(test_index, Qt.DisplayRole) is data_under_test[0]


def test_get_data_success_2():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    test_index = under_test.createIndex(0, 0, data_under_test[0])

    assert under_test.data(test_index, Qt.SizeHintRole) is None


def test_get_data_fail():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    under_test.createIndex(0, 0, data_under_test[0])

    assert under_test.data(QModelIndex(), Qt.DisplayRole) is None


def test_get_flags_fail():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    under_test.createIndex(0, 0, data_under_test[0])

    assert under_test.flags(QModelIndex()) is Qt.NoItemFlags


def test_get_flags_component():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    index = under_test.createIndex(0, 0, data_under_test[0])

    assert under_test.flags(index) == (Qt.ItemIsEnabled | Qt.ItemIsSelectable)


def test_get_flags_component_info():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    item = ComponentInfo(parent=data_under_test[0])
    index = under_test.createIndex(0, 0, item)

    assert under_test.flags(index) == Qt.ItemIsEnabled


def test_get_flags_transformation_list():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    component = data_under_test[0]
    component.stored_transforms = component.transforms
    index = under_test.createIndex(0, 0, component.stored_transforms)

    assert under_test.flags(index) == Qt.ItemIsEnabled | Qt.ItemIsSelectable


def test_get_flags_other():
    data_under_test = FakeInstrument([get_component()])
    under_test = ComponentTreeModel(data_under_test)

    class TestObject:
        pass

    test_item = TestObject()
    index = under_test.createIndex(0, 0, test_item)

    assert (
        under_test.flags(index)
        == Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    )


def test_add_component():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    assert under_test.rowCount(QModelIndex()) == 0
    under_test.add_component(get_component())

    assert under_test.rowCount(QModelIndex()) == 1


def test_add_rotation():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    under_test.add_component(get_component())
    component_index = under_test.index(0, 0, QModelIndex())
    transformation_list_index = under_test.index(1, 0, component_index)
    assert under_test.rowCount(transformation_list_index) == 0
    under_test.add_rotation(component_index)
    assert under_test.rowCount(transformation_list_index) == 1
    transform_index = under_test.index(0, 0, transformation_list_index)
    assert transform_index.internalPointer().type == "Rotation"


def test_add_translation():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    under_test.add_component(get_component())
    component_index = under_test.index(0, 0, QModelIndex())
    transformation_list_index = under_test.index(1, 0, component_index)
    assert under_test.rowCount(transformation_list_index) == 0
    under_test.add_translation(component_index)
    assert under_test.rowCount(transformation_list_index) == 1
    transform_index = under_test.index(0, 0, transformation_list_index)
    assert transform_index.internalPointer().type == "Translation"


def test_add_transformation_alt_1():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    under_test.add_component(get_component())
    component_index = under_test.index(0, 0, QModelIndex())
    transformation_list_index = under_test.index(1, 0, component_index)
    assert under_test.rowCount(transformation_list_index) == 0
    under_test.add_translation(transformation_list_index)
    assert under_test.rowCount(transformation_list_index) == 1


def test_add_transformation_alt_2():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    under_test.add_component(get_component())
    component_index = under_test.index(0, 0, QModelIndex())
    transformation_list_index = under_test.index(1, 0, component_index)
    under_test.add_translation(transformation_list_index)
    assert under_test.rowCount(transformation_list_index) == 1
    transform_index = under_test.index(0, 0, transformation_list_index)
    under_test.add_translation(transform_index)
    assert under_test.rowCount(transformation_list_index) == 2


def test_add_link_alt_1():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    under_test.add_component(get_component())
    component_index = under_test.index(0, 0, QModelIndex())
    transformation_list_index = under_test.index(1, 0, component_index)
    assert under_test.rowCount(transformation_list_index) == 0
    under_test.add_link(component_index)
    assert under_test.rowCount(transformation_list_index) == 1
    assert transformation_list_index.internalPointer().has_link
    assert len(transformation_list_index.internalPointer()) == 0


def test_add_link_alt_2():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    under_test.add_component(get_component())
    component_index = under_test.index(0, 0, QModelIndex())
    transformation_list_index = under_test.index(1, 0, component_index)
    assert under_test.rowCount(transformation_list_index) == 0
    under_test.add_link(transformation_list_index)
    assert under_test.rowCount(transformation_list_index) == 1
    assert transformation_list_index.internalPointer().has_link
    assert len(transformation_list_index.internalPointer()) == 0


def test_add_link_alt_3():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    under_test.add_component(get_component())
    component_index = under_test.index(0, 0, QModelIndex())
    transformation_list_index = under_test.index(1, 0, component_index)
    under_test.add_rotation(component_index)
    transform_index = under_test.index(0, 0, transformation_list_index)
    assert under_test.rowCount(transformation_list_index) == 1
    under_test.add_link(transform_index)
    assert under_test.rowCount(transformation_list_index) == 2
    assert transformation_list_index.internalPointer().has_link
    assert len(transformation_list_index.internalPointer()) == 1


def test_add_link_multiple_times():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    under_test.add_component(get_component())
    component_index = under_test.index(0, 0, QModelIndex())
    transformation_list_index = under_test.index(1, 0, component_index)
    assert under_test.rowCount(transformation_list_index) == 0
    under_test.add_link(component_index)
    first_link = transformation_list_index.internalPointer().link
    under_test.add_link(component_index)
    assert under_test.rowCount(transformation_list_index) == 1
    assert transformation_list_index.internalPointer().has_link
    assert len(transformation_list_index.internalPointer()) == 0
    assert first_link is transformation_list_index.internalPointer().link


def test_duplicate_component():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    assert under_test.rowCount(QModelIndex()) == 0
    under_test.add_component(get_component())
    component_index = under_test.index(0, 0, QModelIndex())
    under_test.duplicate_node(component_index)
    assert under_test.rowCount(QModelIndex()) == 2


def test_duplicate_transform_fail():
    data_under_test = FakeInstrument([])
    under_test = ComponentTreeModel(data_under_test)

    under_test.add_component(get_component())
    component_index = under_test.index(0, 0, QModelIndex())
    under_test.add_rotation(component_index)
    transformation_list_index = under_test.index(1, 0, component_index)
    transformation_index = under_test.index(0, 0, transformation_list_index)
    try:
        under_test.duplicate_node(transformation_index)
    except NotImplementedError:
        return  # Success
    assert False  # Failure


def test_remove_component():
    wrapper = NexusWrapper("test_remove_component")
    instrument = Instrument(wrapper)
    under_test = ComponentTreeModel(instrument)
    instrument.add_component("Some name", "some class", "desc")
    component_index = under_test.index(0, 0, QModelIndex())
    assert under_test.rowCount(QModelIndex()) == 1
    under_test.remove_node(component_index)
    assert under_test.rowCount(QModelIndex()) == 0


def test_remove_transformation():
    wrapper = NexusWrapper("test_remove_transformation")
    instrument = Instrument(wrapper)
    under_test = ComponentTreeModel(instrument)
    instrument.add_component("Some name", "some class", "desc")
    component_index = under_test.index(0, 0, QModelIndex())
    under_test.add_rotation(component_index)
    transformation_list_index = under_test.index(1, 0, component_index)
    transformation_index = under_test.index(0, 0, transformation_list_index)
    assert under_test.rowCount(transformation_list_index) == 1
    under_test.remove_node(transformation_index)
    assert under_test.rowCount(transformation_list_index) == 0


def test_remove_link():
    wrapper = NexusWrapper("test_remove_link")
    instrument = Instrument(wrapper)
    under_test = ComponentTreeModel(instrument)
    instrument.add_component("Some name", "some class", "desc")
    component_index = under_test.index(0, 0, QModelIndex())
    under_test.add_link(component_index)
    transformation_list_index = under_test.index(1, 0, component_index)
    transformation_index = under_test.index(0, 0, transformation_list_index)
    assert under_test.rowCount(transformation_list_index) == 1
    assert len(transformation_list_index.internalPointer()) == 0
    under_test.remove_node(transformation_index)
    assert under_test.rowCount(transformation_list_index) == 0


def test_GIVEN_component_with_cylindrical_shape_information_WHEN_duplicating_component_THEN_shape_information_is_stored_in_nexus_file():
    wrapper = NexusWrapper("test_duplicate_cyl_shape")
    instrument = Instrument(wrapper)

    first_component_name = "component1"
    first_component_nx_class = "NXdetector"
    description = "desc"
    first_component = instrument.add_component(
        first_component_name, first_component_nx_class, description
    )

    axis_direction = QVector3D(1, 0, 0)
    height = 2
    radius = 3
    units = "cm"
    first_component.set_cylinder_shape(
        axis_direction=axis_direction, height=height, radius=radius, units=units
    )
    tree_model = ComponentTreeModel(instrument)

    first_component_index = tree_model.index(0, 0, QModelIndex())
    tree_model.duplicate_node(first_component_index)

    assert tree_model.rowCount(QModelIndex()) == 3
    second_component_index = tree_model.index(2, 0, QModelIndex())
    second_component = second_component_index.internalPointer()
    second_shape = second_component.get_shape()
    assert second_shape.axis_direction == axis_direction
    assert second_shape.height == height
    assert second_shape.units == units
