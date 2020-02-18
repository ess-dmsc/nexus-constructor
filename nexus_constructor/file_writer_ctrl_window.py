from functools import partial

from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import BrokerAndTopicValidator
from ui.Led import Led
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
        # self.settings = QSettings("ess", "nexus-constructor")
        self.instrument = instrument
        self.setupUi()

    def setupUi(self):
        super().setupUi(self)
        self.statusBrokerLed = Led(self)
        self.status_topic_layout.addWidget(self.statusBrokerLed)
        self.statusBrokerLed.turn_on(False)

        validator = BrokerAndTopicValidator()
        self.status_broker_edit.setValidator(validator)
        validator.is_valid.connect(partial(validate_line_edit, self.status_broker_edit))

        self.status_broker_edit.textChanged.connect(self.onTextChanged)
        self.statusBrokerChangeTimer = QTimer()
        self.statusBrokerChangeTimer.setSingleShot(True)
        self.statusBrokerChangeTimer.timeout.connect(self.onTextChangedTimer)
        self.status_consumer = None

        self.commandBrokerLed = Led(self)
        self.command_broker_layout.addWidget(self.commandBrokerLed)
        self.commandBrokerLed.turn_on(False)
        self.command_broker_edit.textChanged.connect(self.onCommandBrokerTextChanged)
        self.commandBrokerChangeTimer = QTimer()
        self.commandBrokerChangeTimer.setSingleShot(True)
        self.commandBrokerChangeTimer.timeout.connect(
            self.onCommandBrokerTextChangeTimer
        )
        self.command_producer = None

        self.command_widget.ok_button.clicked.connect(self.onSendCommand)

        self.updateStatusTimer = QTimer()
        self.updateStatusTimer.timeout.connect(self.onCheckConnectionStatus)
        self.updateStatusTimer.start(500)

        self.files_list.clicked.connect(self.onClickedFileList)
        self.stop_file_writing_button.clicked.connect(self.onStopFileWriting)

        self.model = QStandardItemModel(0, 2, self)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "File writer")
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Last seen")
        self.file_writers_list.setModel(self.model)
        self.file_writers_list.setColumnWidth(0, 320)

        self.fileModel = QStandardItemModel(0, 3, self)
        self.fileModel.setHeaderData(0, QtCore.Qt.Horizontal, "File name")
        self.fileModel.setHeaderData(1, QtCore.Qt.Horizontal, "Last seen")
        self.fileModel.setHeaderData(2, QtCore.Qt.Horizontal, "File writer")
        self.files_list.setModel(self.fileModel)

        self.known_writers = {}
        self.known_files = {}

    def onCheckConnectionStatus(self):
        if self.status_consumer is None:
            self.statusBrokerLed.turn_on(False)
        else:
            connection_ok = self.status_consumer.isConnected()
            self.statusBrokerLed.turn_on(connection_ok)
            if connection_ok:
                current_writers = self.status_consumer.getFilewriters()
                self.updateWriterList(current_writers)
                self.updateFilesList(self.status_consumer.getFiles())

        if self.command_producer is None:
            self.commandBrokerLed.turn_on(False)
            pass
        else:
            self.commandBrokerLed.turn_on(self.command_producer.isConnected())
            pass

    def onTextChanged(self):
        self.statusBrokerChangeTimer.start(1000)

    def onTextChangedTimer(self):
        result = extract_addr_and_topic(self.status_broker_edit.text())
        if result is not None:
            if self.status_consumer is not None:
                self.status_consumer.__del__()
            self.status_consumer = StatusConsumer(*result)

    def onCommandBrokerTextChanged(self):
        self.commandBrokerChangeTimer.start(1000)

    def onCommandBrokerTextChangeTimer(self):
        result = extract_addr_and_topic(self.command_broker_edit.text())
        if result is not None:
            self.brokerLineEdit.setPlaceholderText(result[0])
            if self.command_producer is not None:
                self.command_producer.__del__()
            self.command_producer = CommandProducer(*result)
        else:
            self.brokerLineEdit.setPlaceholderText("address:port")

    def updateWriterList(self, updated_list):
        for key in updated_list:
            current_time = updated_list[key]["last_seen"]
            time_struct = time.localtime(current_time / 1000)
            time_str = time.strftime("%Y-%m-%d %H:%M:%S%Z", time_struct)
            if key not in self.known_writers:
                NrOfFWRows = self.model.rowCount(QtCore.QModelIndex())
                new_file_writer = FileWriter(key, NrOfFWRows)
                self.known_writers[key] = new_file_writer
                self.model.insertRow(NrOfFWRows)
                self.model.setData(self.model.index(NrOfFWRows, 0), key)
                self.model.setData(self.model.index(NrOfFWRows, 1), time_str)
            cFilewriter = self.known_writers[key]
            if current_time != self.known_writers[key].last_time:
                self.model.setData(self.model.index(cFilewriter.row, 1), time_str)
                cFilewriter.last_time = current_time

    def updateFilesList(self, updated_list):
        for key in updated_list:
            current_time = updated_list[key]["last_seen"]
            time_struct = time.localtime(current_time / 1000)
            time_str = time.strftime("%Y-%m-%d %H:%M:%S%Z", time_struct)
            if key not in self.known_files:
                NrOfFWRows = self.fileModel.rowCount(QtCore.QModelIndex())
                writer_id = updated_list[key]["writer_id"]
                file_id = updated_list[key]["file_id"]
                new_file = File(key, NrOfFWRows, writer_id, file_id)
                self.known_files[key] = new_file
                self.fileModel.insertRow(NrOfFWRows)
                self.fileModel.setData(self.fileModel.index(NrOfFWRows, 0), key)
                self.fileModel.setData(self.fileModel.index(NrOfFWRows, 1), time_str)
                self.fileModel.setData(
                    self.fileModel.index(NrOfFWRows, 2), new_file.writer_id
                )
            cFile = self.known_files[key]
            if current_time != self.known_files[key].last_time:
                self.fileModel.setData(self.fileModel.index(cFile.row, 1), time_str)
                cFile.last_time = current_time

    def onFileNameChange(self):
        self.updateCommandPossible()

    def onSendCommand(self):
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
                service_id=None,
                use_swmr=self.useSWMRCheckBox.isChecked(),
            )
            in_memory_file.seek(0)
            send_msg = in_memory_file.read()
            self.command_producer.sendCommand(send_msg)
            self.sendCommandButton.setEnabled(False)

    def onClickedFileList(self):
        if len(self.files_list.selectedIndexes()) > 0:
            self.stop_file_writing_button.setEnabled(True)
        else:
            self.stop_file_writing_button.setEnabled(False)

    def onStopFileWriting(self):
        stopWritingMsgTemplate = (
            """ "cmd": "FileWriter_stop", "job_id": "{}", "service_id": "{}" """
        )
        selected_files = self.files_list.selectedIndexes()
        for indice in selected_files:
            for fileKey in self.known_files:
                cFile = self.known_files[fileKey]
                if indice.row() == cFile.row:
                    send_msg = stopWritingMsgTemplate.format(
                        cFile.job_id, cFile.writer_id
                    )
                    self.command_producer.sendCommand(
                        ("{" + send_msg + "}").encode("utf-8")
                    )
                    break
