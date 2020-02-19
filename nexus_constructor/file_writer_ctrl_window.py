from functools import partial
from typing import Callable, Dict

from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import BrokerAndTopicValidator
from ui.led import Led
from ui.filewriter_ctrl_frame import Ui_FilewriterCtrl
from PySide2.QtWidgets import QMainWindow, QLineEdit
from PySide2.QtCore import QTimer, QAbstractItemModel, QModelIndex
from PySide2.QtGui import QStandardItemModel
from PySide2 import QtCore
from nexus_constructor.instrument import Instrument
from nexus_constructor.kafka.status_consumer import StatusConsumer
from nexus_constructor.kafka.command_producer import CommandProducer
import time
from nexus_constructor.json.filewriter_json_writer import generate_json
import io


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
        self.known_writers = {}
        self.known_files = {}

    def setupUi(self):
        super().setupUi(self)

        self.status_broker_led = Led(self)
        self.status_topic_layout.addWidget(self.status_broker_led)
        self.status_broker_change_timer = QTimer()
        self._set_up_broker_fields(
            self.status_broker_led,
            self.status_broker_edit,
            self.status_broker_change_timer,
            self.status_broker_changed_timer,
        )
        self.status_consumer = None

        self.command_broker_led = Led(self)
        self.command_broker_layout.addWidget(self.command_broker_led)
        self.command_broker_change_timer = QTimer()
        self._set_up_broker_fields(
            self.command_broker_led,
            self.command_broker_edit,
            self.command_broker_change_timer,
            self.command_broker_timer_changed,
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

    @staticmethod
    def _set_up_broker_fields(
        led: Led, edit: QLineEdit, timer: QTimer, timer_callback: Callable
    ):
        led.turn_off()
        validator = BrokerAndTopicValidator()
        edit.setValidator(validator)
        validator.is_valid.connect(partial(validate_line_edit, edit))
        edit.textChanged.connect(lambda: timer.start(1000))
        timer.setSingleShot(True)
        timer.timeout.connect(timer_callback)

    def _check_connection_status(self):
        if self.status_consumer is None:
            self.status_broker_led.turn_off()
        else:
            connection_ok = self.status_consumer.connected
            self.status_broker_led.set_status(connection_ok)
            if connection_ok:
                current_writers = self.status_consumer.file_writers
                self._update_writer_list(current_writers)
                self._update_files_list(self.status_consumer.files)

        if self.command_producer is None:
            self.command_broker_led.turn_off()
        else:
            self.command_broker_led.set_status(self.command_producer.connected)

    def status_broker_changed_timer(self):
        result = BrokerAndTopicValidator.extract_addr_and_topic(
            self.status_broker_edit.text()
        )
        if result is not None:
            if self.status_consumer is not None:
                del self.status_consumer
            self.status_consumer = StatusConsumer(*result)

    def command_broker_timer_changed(self):
        result = BrokerAndTopicValidator.extract_addr_and_topic(
            self.command_broker_edit.text()
        )
        if result is not None:
            self.command_broker_edit.setPlaceholderText(result[0])
            if self.command_producer is not None:
                del self.command_producer
            self.command_producer = CommandProducer(*result)
        else:
            self.command_broker_edit.setPlaceholderText("address:port")

    def _update_writer_list(self, updated_list: Dict[str, Dict]):
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
            current_file_writer = self.known_writers[key]
            if current_time != current_file_writer.last_time:
                self._set_time(self.model, current_file_writer, current_time, time_str)

    def _update_files_list(self, updated_list: Dict[str, Dict]):
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
            current_file = self.known_files[key]
            if current_time != current_file.last_time:
                self._set_time(
                    self.file_list_model, current_file, current_time, time_str
                )

    @staticmethod
    def _set_time(
        model: QAbstractItemModel,
        current_index: QModelIndex,
        current_time: str,
        time_str: str,
    ):
        model.setData(model.index(current_index.row, 1), time_str)
        current_index.last_time = current_time

    def send_command(self):
        if self.command_producer is not None:
            (
                nexus_file_name,
                broker,
                start_time,
                stop_time,
                service_id,
                abort_on_uninitialised_stream,
                use_swmr,
            ) = self.command_widget.get_arguments()
            in_memory_file = io.StringIO()
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
            msg_to_send = in_memory_file.read()
            self.command_producer.send_command(msg_to_send)
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
                current_file = self.known_files[fileKey]
                if index.row() == current_file.row:
                    send_msg = f' "cmd": "FileWriter_stop", "job_id": "{current_file.job_id}", "service_id": "{current_file.writer_id}" '
                    self.command_producer.send_command(
                        f'{{"{send_msg}"}}'.encode("utf-8")
                    )
                    break
