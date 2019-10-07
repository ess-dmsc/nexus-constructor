from PySide2.QtCore import QDateTime
from PySide2.QtWidgets import (
    QDialog,
    QFormLayout,
    QDateTimeEdit,
    QLineEdit,
    QCheckBox,
    QPushButton,
)

TIME_FORMAT = "yyyy MM dd hh:mm:ss"


class FilewriterCommandDialog(QDialog):
    def __init__(self):
        super(FilewriterCommandDialog, self).__init__()
        self.setModal(True)
        self.setLayout(QFormLayout())

        self.nexus_file_name_edit = QLineEdit()

        self.start_time_enabled = QCheckBox()
        self.start_time_picker = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_time_picker.setDisplayFormat(TIME_FORMAT)

        self.stop_time_enabled = QCheckBox()
        self.stop_time_picker = QDateTimeEdit(QDateTime.currentDateTime())
        self.stop_time_picker.setDisplayFormat(TIME_FORMAT)

        self.service_id_lineedit = QLineEdit()
        self.abort_on_unitialised_stream_checkbox = QCheckBox()
        self.use_swmr_checkbox = QCheckBox()
        self.use_swmr_checkbox.setChecked(True)

        self.layout().addRow("nexus_file_name", self.nexus_file_name_edit)
        self.layout().addRow("specify start time?", self.start_time_enabled)
        self.layout().addRow("start_time", self.start_time_picker)
        self.layout().addRow("specify stop time?", self.stop_time_enabled)
        self.layout().addRow("stop_time", self.stop_time_picker)
        self.layout().addRow("service_id", self.service_id_lineedit)
        self.layout().addRow(
            "abort_on_uninitialised_stream", self.abort_on_unitialised_stream_checkbox
        )
        self.layout().addRow("use_hdf_swmr", self.use_swmr_checkbox)

        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.close)
        self.layout().addRow(self.ok_button)

    def get_arguments(self):
        return "", True
