from PySide2.QtWidgets import QDialog, QFormLayout, QDateTimeEdit, QLineEdit, QCheckBox, QPushButton


class FilewriterCommandDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setLayout(QFormLayout())


        self.start_time_picker = QDateTimeEdit()
        self.stop_time_picker = QDateTimeEdit()
        self.service_id_lineedit = QLineEdit()
        self.abort_on_unitialised_stream_checkbox = QCheckBox()
        self.use_swmr_checkbox = QCheckBox()
        self.use_swmr_checkbox.setChecked(True)


        self.layout().addRow("start_time", self.start_time_picker)
        self.layout().addRow("stop_time", self.stop_time_picker)
        self.layout().addRow("service_id", self.service_id_lineedit)
        self.layout().addRow("abort_on_uninitialised_stream", self.abort_on_unitialised_stream_checkbox)
        self.layout().addRow("use_hdf_swmr", self.use_swmr_checkbox)

        self.ok_button = QPushButton()
        self.ok_button.clicked.connect(self.close)
        self.layout().addRow(self.ok_button)
