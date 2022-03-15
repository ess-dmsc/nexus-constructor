from PySide2.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableView,
    QVBoxLayout,
)

from ui.base_table import BaseTableModel


class SampleTableModel(BaseTableModel):
    def are_samples_unique(self):
        pass


class ConfigureSamplesDialog(QDialog):
    def __init__(self, samples):
        super().__init__()
        self.setWindowTitle("Configure Users")
        headings = ["name", "formula", "number of", "mass/volume", "density"]
        self.model = SampleTableModel(headings, samples)

        self.layout = QVBoxLayout()
        self.table_layout = QHBoxLayout()
        self.sample_table = QTableView()
        self.sample_table.setModel(self.model)
        self.sample_table.horizontalHeader().setStretchLastSection(True)
        self.table_layout.addWidget(self.sample_table)

        self.table_buttons_layout = QVBoxLayout()
        self.add_sample_button = QPushButton()
        self.add_sample_button.setText("Add Sample")
        self.add_sample_button.clicked.connect(self._add_sample_clicked)
        self.delete_sample_button = QPushButton()
        self.delete_sample_button.setText("Delete Sample")
        self.delete_sample_button.clicked.connect(self._delete_sample_clicked)
        self.table_buttons_layout.addSpacerItem(
            QSpacerItem(0, 0, vData=QSizePolicy.Expanding)
        )
        self.table_buttons_layout.addWidget(self.add_sample_button)
        self.table_buttons_layout.addWidget(self.delete_sample_button)
        self.table_buttons_layout.addSpacerItem(
            QSpacerItem(0, 0, vData=QSizePolicy.Expanding)
        )
        self.table_layout.addLayout(self.table_buttons_layout)

        self.layout.addLayout(self.table_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self._on_accepted_clicked)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

        self.resize(600, 400)

    def _on_accepted_clicked(self):
        self._complete_table()
        self.accept()

    def _complete_table(self):
        self.button_box.button(self.button_box.Ok).setFocus()

    def _add_sample_clicked(self):
        self.sample_table.model().insertRow(self.model.num_rows)

    def _delete_sample_clicked(self):
        rows_to_remove = set()
        for index in self.sample_table.selectedIndexes():
            rows_to_remove.add(index.row())
        self.sample_table.model().removeRows(list(rows_to_remove))
