import pytest
import numpy as np
from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtWidgets import QWidget
from mock import Mock

from nexus_constructor.array_dataset_table_widget import ArrayDatasetTableWidget


@pytest.fixture(scope="function")
def template(qtbot):
    return QWidget()


@pytest.fixture(scope="function")
def array_dataset_table_widget(qtbot, template):
    array_dataset_table_widget = ArrayDatasetTableWidget()
    template.ui = array_dataset_table_widget
    qtbot.addWidget(template)
    return array_dataset_table_widget


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
