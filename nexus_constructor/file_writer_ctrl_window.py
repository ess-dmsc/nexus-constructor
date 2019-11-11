from ui.Led import Led
from ui.filewriter_ctrl_frame import Ui_FilewriterCtrl
from PySide2.QtWidgets import QMainWindow, QApplication
from PySide2.QtCore import QTimer, QDateTime
from PySide2.QtGui import QStandardItemModel
from PySide2 import QtCore
from nexus_constructor.instrument import Instrument
import re
from nexus_constructor.StatusConsumer import StatusConsumer
from nexus_constructor.CommandProducer import CommandProducer
from PySide2.QtCore import QSettings
import time
from nexus_constructor.json.filewriter_json_writer import generate_json
import io

def extract_addr_and_topic(in_string):
    correct_string_re = re.compile("(\s*((([^/?#:]+)+)(:(\d+))?)/([a-zA-Z0-9._-]+)\s*)")
    match_res = re.match(correct_string_re, in_string)
    if match_res != None:
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
        self.settings = QSettings("ess", "nexus-constructor")
        self.instrument = instrument
        self.setupUi()

    def setupUi(self):
        super().setupUi(self)
        self.statusBrokerLed = Led(self)
        self.statusTopicLayout.addWidget(self.statusBrokerLed)
        self.statusBrokerLed.turn_on(False)

        self.statusBrokerEdit.textChanged.connect(self.onTextChanged)
        self.statusBrokerChangeTimer = QTimer()
        self.statusBrokerChangeTimer.setSingleShot(True)
        self.statusBrokerChangeTimer.timeout.connect(self.onTextChangedTimer)
        self.status_consumer = None

        self.commandBrokerLed = Led(self)
        self.commandBrokerLayout.addWidget(self.commandBrokerLed)
        self.commandBrokerLed.turn_on(False)
        self.commandBrokerEdit.textChanged.connect(self.onCommandBrokerTextChanged)
        self.commandBrokerChangeTimer = QTimer()
        self.commandBrokerChangeTimer.setSingleShot(True)
        self.commandBrokerChangeTimer.timeout.connect(self.onCommandBrokerTextChangeTimer)
        self.command_producer = None

        self.fileNameLineEdit.textChanged.connect(self.onFileNameChange)
        self.sendCommandButton.clicked.connect(self.onSendCommand)

        self.updateStatusTimer = QTimer()
        self.updateStatusTimer.timeout.connect(self.onCheckConnectionStatus)
        self.updateStatusTimer.start(500)
        self.startDateTime.setDateTime(QDateTime.currentDateTime())
        self.stopDateTime.setDateTime(QDateTime.currentDateTime())

        self.useStartTimeCheckBox.stateChanged.connect(self.onClickStartTimeCheckBox)
        self.useStopTimeCheckBox.stateChanged.connect(self.onClickStopTimeCheckBox)

        self.filesList.clicked.connect(self.onClickedFileList)
        self.stopFileWritingButton.clicked.connect(self.onStopFileWriting)

        self.model = QStandardItemModel(0, 2, self)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "File writer")
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Last seen")
        self.fileWritersList.setModel(self.model)
        self.fileWritersList.setColumnWidth(0, 400)

        self.fileModel= QStandardItemModel(0, 3, self)
        self.fileModel.setHeaderData(0, QtCore.Qt.Horizontal, "File name")
        self.fileModel.setHeaderData(1, QtCore.Qt.Horizontal, "Last seen")
        self.fileModel.setHeaderData(2, QtCore.Qt.Horizontal, "File writer")
        self.filesList.setModel(self.fileModel)

        self.known_writers = {}
        self.known_files = {}
        self.restore_settings()

        QApplication.instance().aboutToQuit.connect(self.doCleanup)

    def restore_settings(self):
        self.statusBrokerEdit.setText(self.settings.value("status_broker_addr"))
        self.commandBrokerEdit.setText(self.settings.value("command_broker_addr"))
        temp = self.settings.value("use_swmr", False)
        self.useSWMRCheckBox.setChecked(temp)
        self.useStartTimeCheckBox.setChecked(self.settings.value("use_start_time", False))
        self.useStopTimeCheckBox.setChecked(self.settings.value("use_stop_time", False))
        self.fileNameLineEdit.setText(self.settings.value("file_name"))

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
        else:
            self.commandBrokerLed.turn_on(self.command_producer.isConnected())
        self.updateCommandPossible()


    def onTextChanged(self):
        self.statusBrokerChangeTimer.start(1000)

    def onTextChangedTimer(self):
        result = extract_addr_and_topic(self.statusBrokerEdit.text())
        if result is not None:
            if self.status_consumer is not None:
                self.status_consumer.__del__()
            self.status_consumer = StatusConsumer(*result)

    def onCommandBrokerTextChanged(self):
        self.commandBrokerChangeTimer.start(1000)

    def onCommandBrokerTextChangeTimer(self):
        result = extract_addr_and_topic(self.commandBrokerEdit.text())
        if result is not None:
            self.brokerLineEdit.setPlaceholderText(result[0])
            if self.command_producer is not None:
                self.command_producer.__del__()
            self.command_producer = CommandProducer(*result)
        else:
            self.brokerLineEdit.setPlaceholderText("address:port")

    def onClickStartTimeCheckBox(self):
        self.startDateTime.setEnabled(self.useStartTimeCheckBox.isChecked())

    def onClickStopTimeCheckBox(self):
        self.stopDateTime.setEnabled(self.useStopTimeCheckBox.isChecked())

    def doCleanup(self):
        self.settings.setValue("status_broker_addr", self.statusBrokerEdit.text())
        self.settings.setValue("command_broker_addr", self.commandBrokerEdit.text())
        self.settings.setValue("use_swmr", self.useSWMRCheckBox.isChecked())
        self.settings.setValue("use_start_time", self.useStartTimeCheckBox.isChecked())
        self.settings.setValue("use_stop_time", self.useStopTimeCheckBox.isChecked())
        self.settings.setValue("file_name", self.fileNameLineEdit.text())
        if self.status_consumer is not None:
            self.status_consumer.__del__()
        if self.command_producer is not None:
            self.command_producer.__del__()

    def updateCommandPossible(self):
        if len(self.fileNameLineEdit.text()) > 0 and self.command_producer is not None and self.command_producer.isConnected() and not self.command_producer.hasUnsentMessages():
            self.sendCommandButton.setEnabled(True)
        else:
            self.sendCommandButton.setEnabled(False)

    def updateWriterList(self, updated_list):
        for key in updated_list:
            current_time = updated_list[key]["last_seen"]
            if key not in self.known_writers:
                NrOfFWRows = self.model.rowCount(QtCore.QModelIndex())
                new_file_writer = FileWriter(key, NrOfFWRows)
                self.known_writers[key]= new_file_writer
                self.model.insertRow(NrOfFWRows)
                self.model.setData(self.model.index(NrOfFWRows, 0), key)
                self.model.setData(self.model.index(NrOfFWRows, 1), time.ctime(current_time / 1000))
            cFilewriter = self.known_writers[key]
            if current_time != self.known_writers[key].last_time:
                self.model.setData(self.model.index(cFilewriter.row, 1), time.ctime(current_time / 1000))
                cFilewriter.last_time = current_time

    def updateFilesList(self, updated_list):
        for key in updated_list:
            current_time = updated_list[key]["last_seen"]
            if key not in self.known_files:
                NrOfFWRows = self.fileModel.rowCount(QtCore.QModelIndex())
                writer_id = updated_list[key]["writer_id"]
                file_id = updated_list[key]["file_id"]
                new_file = File(key, NrOfFWRows, writer_id, file_id)
                self.known_files[key]= new_file
                self.fileModel.insertRow(NrOfFWRows)
                self.fileModel.setData(self.fileModel.index(NrOfFWRows, 0), key)
                self.fileModel.setData(self.fileModel.index(NrOfFWRows, 1), time.ctime(current_time / 1000))
                self.fileModel.setData(self.fileModel.index(NrOfFWRows, 2), new_file.writer_id)
            cFile = self.known_files[key]
            if current_time != self.known_files[key].last_time:
                self.fileModel.setData(self.fileModel.index(cFile.row, 1), time.ctime(current_time / 1000))
                cFile.last_time = current_time

    def onFileNameChange(self):
        self.updateCommandPossible()

    def onSendCommand(self):
        if self.command_producer is not None:
            in_memory_file = io.BytesIO()
            broker = self.brokerLineEdit.text()
            if len(broker) == 0:
                broker = self.brokerLineEdit.placeholderText()
            start_time = None
            stop_time = None
            generate_json(data=self.instrument,
                          file=in_memory_file,
                          streams=self.instrument.get_streams(),
                          links=self.instrument.get_links(),
                          nexus_file_name=self.fileNameLineEdit.text(),
                          broker=broker,
                          start_time=start_time,
                          stop_time=stop_time,
                          service_id=None,
                          use_swmr=self.useSWMRCheckBox.isChecked()
                          )
            self.command_producer.sendCommand(self.start_msg)
            self.sendCommandButton.setEnabled(False)

    def onClickedFileList(self):
        if len(self.filesList.selectedIndexes()) > 0:
            self.stopFileWritingButton.setEnabled(True)
        else:
            self.stopFileWritingButton.setEnabled(False)

    def onStopFileWriting(self):
        stopWritingMsgTemplate = """ "cmd": "FileWriter_stop", "job_id": "{}","stop_time": {}, "service_id": "{}" """
        stop_time = int(time.time() * 1000)
        selected_files = self.filesList.selectedIndexes()
        for indice in selected_files:
            for fileKey in self.known_files:
                cFile = self.known_files[fileKey]
                if indice.row() == cFile.row:
                    send_msg = stopWritingMsgTemplate.format(cFile.job_id, stop_time, cFile.writer_id)
                    self.command_producer.sendCommand(("{" + send_msg + "}").encode("utf-8"))
                    break
