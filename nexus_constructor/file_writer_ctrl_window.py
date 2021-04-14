import json
import time
import uuid
from functools import partial
from typing import Callable, Dict, Tuple, Type, Union

import attr
from PySide2 import QtCore
from PySide2.QtCore import QAbstractItemModel, QSettings, QTimer
from PySide2.QtGui import QCloseEvent, QStandardItemModel
from PySide2.QtWidgets import QApplication, QLineEdit, QMainWindow
from streaming_data_types import run_start_pl72, run_stop_6s4t

from nexus_constructor.kafka.command_producer import CommandProducer
from nexus_constructor.kafka.kafka_interface import KafkaInterface
from nexus_constructor.kafka.status_consumer import StatusConsumer
from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import BrokerAndTopicValidator
from ui.filewriter_ctrl_frame import Ui_FilewriterCtrl
from ui.led import Led


@attr.s
class FileWriter:
    name = attr.ib(type=str)
    row = attr.ib()
    last_time = attr.ib(default=0)


@attr.s
class File:
    name = attr.ib(type=str)
    row = attr.ib()
    job_id = attr.ib(type=str, default="Unknown")
    writer_id = attr.ib(type=str, default="Unknown")
    last_time = attr.ib(default=0)


class FileWriterSettings:
    STATUS_BROKER_ADDR = "status_broker_addr"
    COMMAND_BROKER_ADDR = "command_broker_addr"
    FILE_BROKER_ADDR = "file_broker_addr"
    USE_START_TIME = "use_start_time"
    USE_STOP_TIME = "use_stop_time"
    FILE_NAME = "file_name"


def extract_bool_from_qsettings(setting: Union[str, bool]):
    if type(setting) == str:
        setting = setting == "True"
    return setting


class FileWriterCtrl(Ui_FilewriterCtrl, QMainWindow):
    def __init__(self, settings: QSettings):
        super().__init__()
        self.settings = settings
        self.setupUi()
        self.known_writers: Dict[str, FileWriter] = {}
        self.known_files: Dict[str, File] = {}
        self.status_consumer: StatusConsumer = None
        self.command_producer: CommandProducer = None

    def _restore_settings(self):
        """
        Restore persistent broker config settings from file.
        """
        self.status_broker_edit.setText(
            self.settings.value(FileWriterSettings.STATUS_BROKER_ADDR)
        )
        self.command_broker_edit.setText(
            self.settings.value(FileWriterSettings.COMMAND_BROKER_ADDR)
        )
        self.command_widget.broker_line_edit.setText(
            self.settings.value(FileWriterSettings.FILE_BROKER_ADDR)
        )
        self.command_widget.start_time_enabled.setChecked(
            extract_bool_from_qsettings(
                self.settings.value(FileWriterSettings.USE_START_TIME, False)
            )
        )
        self.command_widget.stop_time_enabled.setChecked(
            extract_bool_from_qsettings(
                self.settings.value(FileWriterSettings.USE_STOP_TIME, False)
            )
        )
        self.command_widget.nexus_file_name_edit.setText(
            self.settings.value(FileWriterSettings.FILE_NAME)
        )

    def _store_settings(self):
        """
        Store persistent broker config settings to file.
        """
        self.settings.setValue(
            FileWriterSettings.STATUS_BROKER_ADDR, self.status_broker_edit.text()
        )
        self.settings.setValue(
            FileWriterSettings.COMMAND_BROKER_ADDR, self.command_broker_edit.text()
        )
        self.settings.setValue(
            FileWriterSettings.FILE_BROKER_ADDR,
            self.command_widget.broker_line_edit.text(),
        )
        self.settings.setValue(
            FileWriterSettings.USE_START_TIME,
            self.command_widget.start_time_enabled.isChecked(),
        )
        self.settings.setValue(
            FileWriterSettings.USE_STOP_TIME,
            self.command_widget.stop_time_enabled.isChecked(),
        )
        self.settings.setValue(
            FileWriterSettings.FILE_NAME,
            self.command_widget.nexus_file_name_edit.text(),
        )

    def setupUi(self):
        super().setupUi(self)

        self.status_consumer = None
        self.status_broker_led = Led(self)
        self.status_topic_layout.addWidget(self.status_broker_led)
        self.status_broker_change_timer = QTimer()
        self._set_up_broker_fields(
            self.status_broker_led,
            self.status_broker_edit,
            self.status_broker_change_timer,
            self.status_broker_timer_changed,
            StatusConsumer,
        )

        self.command_producer = None

        self.command_broker_led = Led(self)
        self.command_broker_layout.addWidget(self.command_broker_led)
        self.command_broker_change_timer = QTimer()
        self._set_up_broker_fields(
            self.command_broker_led,
            self.command_broker_edit,
            self.command_broker_change_timer,
            self.command_broker_timer_changed,
            CommandProducer,
        )

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
        self._restore_settings()
        QApplication.instance().aboutToQuit.connect(self._store_settings)

    @staticmethod
    def _set_up_broker_fields(
        led: Led,
        edit: QLineEdit,
        timer: QTimer,
        timer_callback: Callable,
        kafka_obj_type: Type[KafkaInterface],
    ):
        led.turn_off()
        validator = BrokerAndTopicValidator()
        edit.setValidator(validator)
        validator.is_valid.connect(partial(validate_line_edit, edit))
        edit.textChanged.connect(lambda: timer.start(1000))
        timer.setSingleShot(True)
        timer.timeout.connect(partial(timer_callback, kafka_obj_type))

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

    def status_broker_timer_changed(self, kafka_obj_type: KafkaInterface):
        result = BrokerAndTopicValidator.extract_addr_and_topic(
            self.status_broker_edit.text()
        )
        if result is not None:
            if self.status_consumer is not None:
                self.status_consumer.close()
            self.status_consumer = StatusConsumer(*result)

    def command_broker_timer_changed(self, kafka_obj_type: KafkaInterface):
        result = BrokerAndTopicValidator.extract_addr_and_topic(
            self.command_broker_edit.text()
        )
        if result is not None:
            if self.command_producer is not None:
                self.command_producer.close()
            self.command_producer = CommandProducer(*result)

    def _update_writer_list(self, updated_list: Dict[str, Dict]):
        for key in updated_list:
            current_time, time_str = self.get_time(key, updated_list)
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
            current_time, time_str = self.get_time(key, updated_list)
            if key not in self.known_files:
                number_of_file_rows = self.file_list_model.rowCount(
                    QtCore.QModelIndex()
                )
                new_file = File(key, row=number_of_file_rows)
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
    def get_time(key: str, updated_list: Dict[str, Dict]) -> Tuple[int, str]:
        current_time = updated_list[key]["last_seen"]
        time_struct = time.localtime(current_time / 1000)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S%Z", time_struct)
        return current_time, time_str

    @staticmethod
    def _set_time(
        model: QAbstractItemModel,
        current_index: Union[File, FileWriter],
        current_time: int,
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
            ) = self.command_widget.get_arguments()
            self.command_producer.send_command(
                bytes(
                    run_start_pl72.serialise_pl72(
                        job_id=str(uuid.uuid4()),
                        filename=nexus_file_name,
                        start_time=start_time,
                        stop_time=stop_time,
                        broker=broker,
                        nexus_structure=json.dumps(self.model.as_dict()),
                        service_id=service_id,
                    )
                )
            )
            self.command_widget.ok_button.setEnabled(False)

    def file_list_clicked(self):
        if len(self.files_list.selectedIndexes()) > 0:
            self.stop_file_writing_button.setEnabled(True)
        else:
            self.stop_file_writing_button.setEnabled(False)

    def stop_file_writing_clicked(self):
        if not self.command_producer:
            return
        selected_files = self.files_list.selectedIndexes()
        for index in selected_files:
            for fileKey in self.known_files:
                current_file = self.known_files[fileKey]
                if index.row() == current_file.row:
                    self.command_producer.send_command(
                        bytes(
                            run_stop_6s4t.serialise_6s4t(
                                job_id=current_file.job_id,
                                service_id=current_file.writer_id,
                            )
                        )
                    )
                    break

    def closeEvent(self, event: QCloseEvent):
        if self.status_consumer is not None:
            self.status_consumer.close()
        if self.command_producer is not None:
            self.command_producer.close()
