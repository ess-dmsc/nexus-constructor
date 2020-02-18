from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QLineEdit

from nexus_constructor.filewriter_command_widget import FilewriterCommandWidget


class Ui_FilewriterCtrl(object):
    def setupUi(self, FilewriterCtrl):
        FilewriterCtrl.resize(649, 450)
        self.centralwidget = QtWidgets.QWidget(FilewriterCtrl)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.statusLayout = QtWidgets.QVBoxLayout()
        self.statusLayout.setContentsMargins(-1, -1, -1, 0)
        self.statusTopicLayout = QtWidgets.QHBoxLayout()
        self.statusTopicLayout.setContentsMargins(-1, -1, -1, 0)
        self.statusBrokerLabel = QtWidgets.QLabel(self.centralwidget)
        self.statusTopicLayout.addWidget(self.statusBrokerLabel)
        self.statusBrokerEdit = QLineEdit(self.centralwidget)
        self.statusBrokerEdit.setPlaceholderText("address:port/topic")

        self.statusTopicLayout.addWidget(self.statusBrokerEdit)
        self.statusLayout.addLayout(self.statusTopicLayout)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.statusLayout.addWidget(self.line_2)
        self.fileWriterTableGroup = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.fileWriterTableGroup.sizePolicy().hasHeightForWidth()
        )
        self.fileWriterTableGroup.setSizePolicy(sizePolicy)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.fileWriterTableGroup)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.fileWritersList = QtWidgets.QTreeView(self.fileWriterTableGroup)
        self.fileWritersList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.fileWritersList.setIndentation(0)
        self.verticalLayout_3.addWidget(self.fileWritersList)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.statusLayout.addWidget(self.fileWriterTableGroup)
        self.filesGroup = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.filesGroup.sizePolicy().hasHeightForWidth())
        self.filesGroup.setSizePolicy(sizePolicy)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.filesGroup)
        self.filesList = QtWidgets.QTreeView(self.filesGroup)
        self.filesList.setIndentation(0)
        self.verticalLayout_6.addWidget(self.filesList)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_4.addItem(spacerItem)
        self.stopFileWritingButton = QtWidgets.QPushButton(self.filesGroup)
        self.stopFileWritingButton.setEnabled(False)
        self.horizontalLayout_4.addWidget(self.stopFileWritingButton)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.statusLayout.addWidget(self.filesGroup)
        self.horizontalLayout.addLayout(self.statusLayout)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line)

        self.commandLayout = QtWidgets.QVBoxLayout()
        self.commandLayout.setContentsMargins(-1, 0, -1, 0)
        self.commandBrokerLayout = QtWidgets.QHBoxLayout()
        self.commandBrokerLabel = QtWidgets.QLabel(self.centralwidget)
        self.commandBrokerLayout.addWidget(self.commandBrokerLabel)
        self.commandBrokerEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.commandBrokerLayout.addWidget(self.commandBrokerEdit)
        self.commandLayout.addLayout(self.commandBrokerLayout)

        self.command_widget = FilewriterCommandWidget()
        self.commandLayout.addWidget(self.command_widget)

        self.horizontalLayout.addLayout(self.commandLayout)

        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        FilewriterCtrl.setCentralWidget(self.centralwidget)

        FilewriterCtrl.setWindowTitle("MainWindow")
        self.statusBrokerLabel.setText("Status broker")
        self.fileWriterTableGroup.setTitle("File-writers")
        self.filesGroup.setTitle("Files")
        self.stopFileWritingButton.setText("Stop file-writing")
        self.commandBrokerLabel.setText("Command broker")
        self.commandBrokerEdit.setPlaceholderText("address:port/topic")

        QtCore.QMetaObject.connectSlotsByName(FilewriterCtrl)
