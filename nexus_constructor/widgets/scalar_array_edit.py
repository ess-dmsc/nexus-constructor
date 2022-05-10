from PySide2.QtWidgets import QWidget, QPushButton, QDialog, QGridLayout
from PySide2.QtCore import Qt

from nexus_constructor.model import Dataset
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP
from nexus_constructor.array_dataset_table_widget import ArrayDatasetTableWidget
from .scalar_value_base import ScalarValueBase
import numpy as np


class ScalarArrayEdit(ScalarValueBase):
    def __init__(self, parent: QWidget, dataset: Dataset):
        super().__init__(parent, dataset)
        self._edit_button = QPushButton("Edit")
        self.layout().insertWidget(0, self._edit_button)
        self._edit_button.clicked.connect(self._show_edit_dialog)

    def _show_edit_dialog(self):
        self._edit_dialog = QDialog(parent=self.parent())
        self._edit_dialog.setWindowModality(Qt.WindowModal)
        self._edit_dialog.setLayout(QGridLayout())
        np_type = VALUE_TYPE_TO_NP[self._value_type_combo.currentText()]
        self._table_view = ArrayDatasetTableWidget(np_type)
        self._table_view.model.update_array_dtype(np_type)
        if isinstance(self._dataset.values, np.ndarray):
            self._table_view.model.array = self._dataset.values
        else:
            self._table_view.model.array = np.array([[self._dataset.values, ]], dtype=np_type)
        self._edit_dialog.layout().addWidget(self._table_view)
        self._edit_done_button = QPushButton("Done")
        self._edit_dialog.layout().addWidget(self._edit_done_button)
        self._edit_done_button.clicked.connect(self._done_editing)
        self._edit_dialog.show()

    def _done_editing(self):
        self._edit_dialog.close()
        self._dataset.values = self._table_view.model.array


    def _value_changed(self, new_value: str):
        try:
            self._dataset.values = VALUE_TYPE_TO_NP[
                self._value_type_combo.currentText()
            ](new_value)
        except ValueError:
            self._dataset.values = new_value

    def check_validity(self):
        super().check_validity()
