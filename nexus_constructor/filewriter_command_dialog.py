from functools import partial
from typing import Union, Tuple

from PySide2.QtCore import QDateTime, Qt
from PySide2.QtWidgets import (
    QFormLayout,
    QDateTimeEdit,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QWidget,
)

from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import (
    CommandDialogFileNameValidator,
    HDF_FILE_EXTENSIONS,
    NameValidator,
    CommandDialogOKValidator,
)

TIME_FORMAT = "yyyy MM dd hh:mm:ss"


class FilewriterCommandWidget(QWidget):
    """
    Used for the required and optional fields when saving a filewriter command JSON file.
    """

    def __init__(self, parent=None):
        super(FilewriterCommandWidget, self).__init__()
        self.setParent(parent)
        self.setLayout(QFormLayout())

        self.nexus_file_name_edit = QLineEdit()

        self.ok_button = QPushButton("Ok")
        if parent is not None:
            self.ok_button.clicked.connect(parent.close)

        self.broker_line_edit = QLineEdit()
        self.broker_line_edit.setPlaceholderText("broker:port")

        self.ok_validator = CommandDialogOKValidator()
        self.ok_validator.is_valid.connect(self.ok_button.setEnabled)

        filename_validator = CommandDialogFileNameValidator()
        self.nexus_file_name_edit.setValidator(filename_validator)
        filename_validator.is_valid.connect(
            partial(
                validate_line_edit,
                self.nexus_file_name_edit,
                tooltip_on_reject=f"Invalid NeXus file name - Should end with {HDF_FILE_EXTENSIONS}",
            )
        )
        filename_validator.is_valid.connect(self.ok_validator.set_filename_valid)
        filename_validator.is_valid.emit(False)

        broker_validator = NameValidator([])
        self.broker_line_edit.setValidator(broker_validator)
        broker_validator.is_valid.connect(
            partial(
                validate_line_edit,
                self.broker_line_edit,
                tooltip_on_reject="Broker is required",
            )
        )
        broker_validator.is_valid.connect(self.ok_validator.set_broker_valid)
        broker_validator.is_valid.emit(False)

        self.start_time_enabled = QCheckBox()
        self.start_time_picker = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_time_picker.setDisplayFormat(TIME_FORMAT)
        self.start_time_enabled.stateChanged.connect(partial(self.state_changed, True))
        self.start_time_enabled.setChecked(True)

        self.stop_time_enabled = QCheckBox()
        self.stop_time_picker = QDateTimeEdit(QDateTime.currentDateTime())
        self.stop_time_picker.setDisplayFormat(TIME_FORMAT)
        self.stop_time_enabled.stateChanged.connect(partial(self.state_changed, False))
        self.stop_time_enabled.setChecked(False)

        self.service_id_lineedit = QLineEdit()
        self.service_id_lineedit.setPlaceholderText("(Optional)")
        self.abort_on_uninitialised_stream_checkbox = QCheckBox()
        self.use_swmr_checkbox = QCheckBox()
        self.use_swmr_checkbox.setChecked(True)

        self.layout().addRow("nexus_file_name", self.nexus_file_name_edit)
        self.layout().addRow("broker", self.broker_line_edit)
        self.layout().addRow("specify start time?", self.start_time_enabled)
        self.layout().addRow("start_time", self.start_time_picker)
        self.layout().addRow("specify stop time?", self.stop_time_enabled)
        self.layout().addRow("stop_time", self.stop_time_picker)
        self.layout().addRow("service_id", self.service_id_lineedit)
        self.layout().addRow(
            "abort_on_uninitialised_stream", self.abort_on_uninitialised_stream_checkbox
        )
        self.layout().addRow("use_hdf_swmr", self.use_swmr_checkbox)
        self.layout().addRow(self.ok_button)

    def state_changed(self, is_start_time: bool, state: Qt.CheckState):
        if state != Qt.CheckState.Checked:
            self.start_time_picker.setEnabled(
                False
            ) if is_start_time else self.stop_time_picker.setEnabled(False)
        else:
            self.start_time_picker.setEnabled(
                True
            ) if is_start_time else self.stop_time_picker.setEnabled(True)

    def get_arguments(
        self,
    ) -> Tuple[str, str, Union[str, None], Union[str, None], str, bool, bool]:
        """
        gets the arguments of required and optional fields for the filewriter command.
        :return: Tuple containing all of the fields.
        """
        return (
            self.nexus_file_name_edit.text(),
            self.broker_line_edit.text(),
            self.start_time_picker.dateTime().toMSecsSinceEpoch()
            if self.start_time_enabled.checkState() == Qt.CheckState.Checked
            else None,
            self.stop_time_picker.dateTime().toMSecsSinceEpoch()
            if self.stop_time_enabled.checkState() == Qt.CheckState.Checked
            else None,
            self.service_id_lineedit.text(),
            self.abort_on_uninitialised_stream_checkbox.checkState()
            == Qt.CheckState.Checked,
            self.use_swmr_checkbox.checkState() == Qt.CheckState.Checked,
        )
