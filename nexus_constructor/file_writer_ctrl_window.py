from functools import partial

from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import BrokerAndTopicValidator
from ui.led import Led
from ui.filewriter_ctrl_frame import Ui_FilewriterCtrl
from PySide2.QtWidgets import QMainWindow
from PySide2.QtCore import QTimer
from PySide2.QtGui import QStandardItemModel
from PySide2 import QtCore
from nexus_constructor.instrument import Instrument
import re
from nexus_constructor.StatusConsumer import StatusConsumer
from nexus_constructor.CommandProducer import CommandProducer
import time
from nexus_constructor.json.filewriter_json_writer import generate_json
import io


def extract_addr_and_topic(in_string):
    correct_string_re = re.compile(
        "(\s*((([^/?#:]+)+)(:(\d+))?)/([a-zA-Z0-9._-]+)\s*)"
    )  # noqa: W605
    match_res = re.match(correct_string_re, in_string)
    if match_res is not None:
        return match_res.group(2), match_res.group(7)
    return None


class FileWriter:
    def __init__(self, name, row):
        self.name = name
        self.row = row
        self.last_time = 0


class File:
    def __init__(self, name, row, writer_id, job_id):
        self.name = name
        self.row = row
        self.writer_id = writer_id
        self.job_id = job_id
        self.last_time = 0


class FileWriterCtrl(Ui_FilewriterCtrl, QMainWindow):
    def __init__(self, instrument: Instrument):
        super().__init__()
        self.instrument = instrument
        self.setupUi()

    def setupUi(self):
        super().setupUi(self)
        self.status_broker_led = Led(self)
        self.status_topic_layout.addWidget(self.status_broker_led)
        self.status_broker_led.turn_on(False)

        validator = BrokerAndTopicValidator()
        self.status_broker_edit.setValidator(validator)
        validator.is_valid.connect(partial(validate_line_edit, self.status_broker_edit))

        self.status_broker_edit.textChanged.connect(
            lambda: self.status_broker_change_timer.start(1000)
        )
        self.status_broker_change_timer = QTimer()
        self.status_broker_change_timer.setSingleShot(True)
        self.status_broker_change_timer.timeout.connect(self._text_changed_timer)
        self.status_consumer = None

        self.command_broker_led = Led(self)
        self.command_broker_layout.addWidget(self.command_broker_led)
        self.command_broker_led.turn_on(False)
        self.command_broker_edit.textChanged.connect(
            lambda: self.command_broker_change_timer.start(1000)
        )
        self.command_broker_change_timer = QTimer()
        self.command_broker_change_timer.setSingleShot(True)
        self.command_broker_change_timer.timeout.connect(
            self.command_broker_timer_changed
        )
        self.command_producer = None
        self.command_widget.ok_button.clicked.connect(self.send_command)

        self.update_status_timer = QTimer()
        self.update_status_timer.timeout.connect(self._check_connection_status)
        self.update_status_timer.start(500)

        self.files_list.clicked.connect(self.file_list_clicked)
        self.stop_file_writing_button.clicked.connect(self.stop_file_writing_clicked)

        self.model = QStandardItemModel(0, 2, self)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "File writer")
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Last seen")
        self.file_writers_list.setModel(self.model)
        self.file_writers_list.setColumnWidth(0, 320)

        self.file_list_model = QStandardItemModel(0, 3, self)
        self.file_list_model.setHeaderData(0, QtCore.Qt.Horizontal, "File name")
        self.file_list_model.setHeaderData(1, QtCore.Qt.Horizontal, "Last seen")
        self.file_list_model.setHeaderData(2, QtCore.Qt.Horizontal, "File writer")
        self.files_list.setModel(self.file_list_model)

        self.known_writers = {}
        self.known_files = {}

    def _check_connection_status(self):
        if self.status_consumer is None:
            self.status_broker_led.turn_on(False)
        else:
            connection_ok = self.status_consumer.isConnected()
            self.status_broker_led.turn_on(connection_ok)
            if connection_ok:
                current_writers = self.status_consumer.getFilewriters()
                self._update_writer_list(current_writers)
                self._update_files_list(self.status_consumer.getFiles())

        if self.command_producer is None:
            self.command_broker_led.turn_on(False)
        else:
            self.command_broker_led.turn_on(self.command_producer.isConnected())

    def _text_changed_timer(self):
        result = extract_addr_and_topic(self.status_broker_edit.text())
        if result is not None:
            if self.status_consumer is not None:
                self.status_consumer.__del__()
            self.status_consumer = StatusConsumer(*result)

    def command_broker_timer_changed(self):
        result = extract_addr_and_topic(self.command_broker_edit.text())
        if result is not None:
            self.command_broker_edit.setPlaceholderText(result[0])
            if self.command_producer is not None:
                del self.command_producer
            self.command_producer = CommandProducer(*result)
        else:
            self.command_broker_edit.setPlaceholderText("address:port")

    def _update_writer_list(self, updated_list):
        for key in updated_list:
            current_time = updated_list[key]["last_seen"]
            time_struct = time.localtime(current_time / 1000)
            time_str = time.strftime("%Y-%m-%d %H:%M:%S%Z", time_struct)
            if key not in self.known_writers:
                number_of_filewriter_rows = self.model.rowCount(QtCore.QModelIndex())
                new_file_writer = FileWriter(key, number_of_filewriter_rows)
                self.known_writers[key] = new_file_writer
                self.model.insertRow(number_of_filewriter_rows)
                self.model.setData(self.model.index(number_of_filewriter_rows, 0), key)
                self.model.setData(
                    self.model.index(number_of_filewriter_rows, 1), time_str
                )
            cFilewriter = self.known_writers[key]
            if current_time != cFilewriter.last_time:
                self.model.setData(self.model.index(cFilewriter.row, 1), time_str)
                cFilewriter.last_time = current_time

    def _update_files_list(self, updated_list):
        for key in updated_list:
            current_time = updated_list[key]["last_seen"]
            time_struct = time.localtime(current_time / 1000)
            time_str = time.strftime("%Y-%m-%d %H:%M:%S%Z", time_struct)
            if key not in self.known_files:
                number_of_file_rows = self.file_list_model.rowCount(
                    QtCore.QModelIndex()
                )
                writer_id = updated_list[key]["writer_id"]
                file_id = updated_list[key]["file_id"]
                new_file = File(key, number_of_file_rows, writer_id, file_id)
                self.known_files[key] = new_file
                self.file_list_model.insertRow(number_of_file_rows)
                self.file_list_model.setData(
                    self.file_list_model.index(number_of_file_rows, 0), key
                )
                self.file_list_model.setData(
                    self.file_list_model.index(number_of_file_rows, 1), time_str
                )
                self.file_list_model.setData(
                    self.file_list_model.index(number_of_file_rows, 2),
                    new_file.writer_id,
                )
            cFile = self.known_files[key]
            if current_time != cFile.last_time:
                self.file_list_model.setData(
                    self.file_list_model.index(cFile.row, 1), time_str
                )
                cFile.last_time = current_time

    def send_command(self):
        if self.command_producer is not None:
            in_memory_file = io.StringIO()

            (
                nexus_file_name,
                broker,
                start_time,
                stop_time,
                service_id,
                abort_on_uninitialised_stream,
                use_swmr,
            ) = self.command_widget.get_arguments()

            generate_json(
                data=self.instrument,
                file=in_memory_file,
                nexus_file_name=nexus_file_name,
                broker=broker,
                start_time=start_time,
                stop_time=stop_time,
                service_id=service_id,
                use_swmr=use_swmr,
            )
            in_memory_file.seek(0)
            send_msg = in_memory_file.read()
            self.command_producer.sendCommand(send_msg)
            self.command_widget.ok_button.setEnabled(False)

    def file_list_clicked(self):
        if len(self.files_list.selectedIndexes()) > 0:
            self.stop_file_writing_button.setEnabled(True)
        else:
            self.stop_file_writing_button.setEnabled(False)

    def stop_file_writing_clicked(self):
        selected_files = self.files_list.selectedIndexes()
        for index in selected_files:
            for fileKey in self.known_files:
                cFile = self.known_files[fileKey]
                if index.row() == cFile.row:
                    send_msg = f' "cmd": "FileWriter_stop", "job_id": "{cFile.job_id}", "service_id": "{cFile.writer_id}" '
                    self.command_producer.sendCommand(
                        f'{{"{send_msg}"}}'.encode("utf-8")
                    )
                    break
