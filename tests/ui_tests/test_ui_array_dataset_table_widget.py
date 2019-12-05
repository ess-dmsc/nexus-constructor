import pytest
from PySide2.QtWidgets import QWidget

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
