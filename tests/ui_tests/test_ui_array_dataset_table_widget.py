import numpy as np
import pytest
from mock import Mock
from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt

from nexus_constructor.array_dataset_table_widget import ArrayDatasetTableWidget
from nexus_constructor.model.value_type import ValueTypes
from nexus_constructor.validators import VALUE_TYPE_TO_NP


@pytest.fixture(scope="function")
def array_dataset_table_widget(qtbot, template):
    array_dataset_table_widget = ArrayDatasetTableWidget()
    template.ui = array_dataset_table_widget
    qtbot.addWidget(template)
    return array_dataset_table_widget


@pytest.mark.skip(reason="Pyside6 issue")
@pytest.mark.parametrize("array_shape", [(6, 1), (1, 6), (6,), (6, 6)])
def test_UI_GIVEN_data_has_different_shapes_WHEN_getting_array_from_component_THEN_data_returns_correct_value(
    array_dataset_table_widget, array_shape
):

    model_index = Mock(spec=QModelIndex)
    last_value_x = array_shape[0] - 1
    model_index.row.return_value = last_value_x
    value_index = (last_value_x,)

    array_size = array_shape[0]

    if len(array_shape) > 1:
        array_size *= array_shape[1]
        last_value_y = array_shape[1] - 1
        model_index.column.return_value = last_value_y
        value_index = (last_value_x, last_value_y)

    array = np.arange(array_size).reshape(array_shape)
    array_dataset_table_widget.model.array = array

    assert array_dataset_table_widget.model.data(model_index, Qt.DisplayRole) == str(
        array[value_index]
    )


@pytest.mark.parametrize("orig_data_type", VALUE_TYPE_TO_NP.values())
@pytest.mark.parametrize("new_data_type", VALUE_TYPE_TO_NP.values())
def test_UI_GIVEN_data_type_WHEN_changing_data_type_THEN_change_is_successful(
    array_dataset_table_widget, orig_data_type, new_data_type
):

    array = np.arange(10).astype(orig_data_type)
    array_dataset_table_widget.model.array = array
    array_dataset_table_widget.model.update_array_dtype(new_data_type)

    if new_data_type is not str:
        assert array_dataset_table_widget.model.array.dtype == new_data_type
    else:
        assert "<U" in str(array_dataset_table_widget.model.array.dtype)


def test_GIVEN_string_array_WHEN_changing_data_type_to_int_THEN_array_rests(
    array_dataset_table_widget,
):
    array = np.array(["hello" for _ in range(10)])
    array_dataset_table_widget.model.array = array
    array_dataset_table_widget.model.update_array_dtype(
        VALUE_TYPE_TO_NP[ValueTypes.INT]
    )

    assert array_dataset_table_widget.model.array.item(0) == 0


def test_UI_GIVEN_add_row_button_pressed_THEN_array_size_changes(
    array_dataset_table_widget,
):

    array_dataset_table_widget.add_row_button.trigger()
    assert array_dataset_table_widget.model.array.shape == (2, 1)


def test_UI_GIVEN_add_column_button_pressed_THEN_array_size_changes(
    array_dataset_table_widget,
):

    array_dataset_table_widget.add_column_button.trigger()
    assert array_dataset_table_widget.model.array.shape == (1, 2)


def test_UI_GIVEN_remove_row_button_pressed_WHEN_table_has_more_than_one_row_THEN_array_size_changes(
    array_dataset_table_widget,
):

    array_dataset_table_widget.add_row_button.trigger()
    selection_index = array_dataset_table_widget.model.index(1, 0)
    array_dataset_table_widget.view.selectionModel().select(
        selection_index, QItemSelectionModel.Select
    )
    array_dataset_table_widget.remove_row_button.trigger()

    assert array_dataset_table_widget.model.array.shape == (1, 1)


def test_UI_GIVEN_remove_column_button_pressed_WHEN_table_has_more_than_one_column_THEN_array_size_changes(
    array_dataset_table_widget, qtbot
):
    array_dataset_table_widget.add_column_button.trigger()
    selection_index = array_dataset_table_widget.model.index(0, 1)
    array_dataset_table_widget.view.selectionModel().select(
        selection_index, QItemSelectionModel.Select
    )
    array_dataset_table_widget.remove_column_button.trigger()

    assert array_dataset_table_widget.model.array.shape == (1, 1)


def test_UI_GIVEN_remove_row_button_pressed_WHEN_table_has_one_row_THEN_array_size_is_unchanged(
    array_dataset_table_widget,
):
    selection_index = array_dataset_table_widget.model.index(0, 0)
    array_dataset_table_widget.view.selectionModel().select(
        selection_index, QItemSelectionModel.Select
    )
    array_dataset_table_widget.remove_row_button.trigger()

    assert array_dataset_table_widget.model.array.shape == (1, 1)


def test_UI_GIVEN_remove_column_button_pressed_WHEN_table_has_one_column_THEN_array_size_is_unchanged(
    array_dataset_table_widget,
):
    selection_index = array_dataset_table_widget.model.index(0, 0)
    array_dataset_table_widget.view.selectionModel().select(
        selection_index, QItemSelectionModel.Select
    )
    array_dataset_table_widget.remove_column_button.trigger()

    assert array_dataset_table_widget.model.array.shape == (1, 1)


def test_UI_GIVEN_data_is_entered_WHEN_data_and_index_are_valid_THEN_array_changes(
    array_dataset_table_widget,
):

    selection_index = array_dataset_table_widget.model.index(0, 0)
    data = 3
    array_dataset_table_widget.model.setData(selection_index, data, Qt.EditRole)
    assert array_dataset_table_widget.model.array[0][0] == data


def test_UI_GIVEN_data_is_entered_WHEN_data_index_is_invalid_THEN_set_data_returns_false(
    array_dataset_table_widget,
):

    selection_index = array_dataset_table_widget.model.index(5, 5)
    assert not array_dataset_table_widget.model.setData(selection_index, 3, Qt.EditRole)


def test_UI_GIVEN_data_is_single_column_WHEN_adding_row_THEN_data_is_resized_in_order_to_add_row(
    array_dataset_table_widget,
):

    array = np.arange(10)
    array_dataset_table_widget.model.array = array
    array_dataset_table_widget.model.add_row()
    assert array_dataset_table_widget.model.array.shape == (11, 1)
