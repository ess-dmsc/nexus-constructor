from functools import partial
from typing import Union, Tuple

from PySide2.QtCore import QDateTime, Qt, Signal
from PySide2.QtGui import QValidator
from PySide2.QtWidgets import (
    QDialog,
    QFormLayout,
    QDateTimeEdit,
    QLineEdit,
    QCheckBox,
    QPushButton,
)

from nexus_constructor.ui_utils import validate_line_edit

TIME_FORMAT = "yyyy MM dd hh:mm:ss"


class FilewriterCommandDialog(QDialog):
    def __init__(self):
        super(FilewriterCommandDialog, self).__init__()
        self.setModal(True)
        self.setLayout(QFormLayout())

        self.nexus_file_name_edit = QLineEdit()
        filename_validator = CommandDialogOKButtonValidator(self)
        self.nexus_file_name_edit.setValidator(filename_validator)
        filename_validator.is_valid.connect(self.validate)
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.close)

        self.validate(False)

        self.start_time_enabled = QCheckBox()
        self.start_time_picker = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_time_picker.setDisplayFormat(TIME_FORMAT)
        self.start_time_enabled.stateChanged.connect(partial(self.state_changed, True))
        self.start_time_enabled.setChecked(True)

        self.stop_time_enabled = QCheckBox()
        self.stop_time_picker = QDateTimeEdit(QDateTime.currentDateTime())
        self.stop_time_picker.setDisplayFormat(TIME_FORMAT)
        self.stop_time_enabled.stateChanged.connect(partial(self.state_changed, False))
        self.stop_time_enabled.setChecked(True)

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
        self.layout().addRow(self.ok_button)

    def validate(self, is_valid):
        self.ok_button.setEnabled(is_valid)
        validate_line_edit(
            self.nexus_file_name_edit,
            is_valid,
            tooltip_on_reject="Invalid NeXus file name",
        )

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
        self
    ) -> Tuple[str, Union[str, None], Union[str, None], str, bool, bool]:
        """
        gets the arguments of required and optional fields for the filewriter command. 
        :return: Tuple containing all of the fields. 
        """
        return (
            self.nexus_file_name_edit.text(),
            self.start_time_picker.dateTime().toMSecsSinceEpoch()
            if self.start_time_enabled.checkState() == Qt.CheckState.Checked
            else None,
            self.stop_time_picker.dateTime().toMSecsSinceEpoch()
            if self.stop_time_enabled.checkState() == Qt.CheckState.Checked
            else None,
            self.service_id_lineedit.text(),
            self.abort_on_unitialised_stream_checkbox.checkState()
            == Qt.CheckState.Checked,
            self.use_swmr_checkbox.checkState() == Qt.CheckState.Checked,
        )


class CommandDialogOKButtonValidator(QValidator):
    """
    Validator to ensure item names are unique within a model that has a 'name' property

    The validationFailed signal is emitted if an entered name is not unique.
    """

    def __init__(self, dialog: FilewriterCommandDialog):
        super().__init__()
        self.dialog = dialog

    def validate(self, input: str, pos: int):
        if not input or not input.endswith("nxs"):
            self.is_valid.emit(False)
            return QValidator.Intermediate

        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)
