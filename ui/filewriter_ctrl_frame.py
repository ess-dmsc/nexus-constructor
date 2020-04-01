from PySide2.QtCore import QMetaObject
from PySide2.QtWidgets import (
    QVBoxLayout,
    QTreeView,
    QAbstractItemView,
    QGroupBox,
    QFrame,
    QSizePolicy,
    QLabel,
    QHBoxLayout,
    QWidget,
    QSpacerItem,
    QPushButton,
    QLineEdit,
)

from nexus_constructor.filewriter_command_widget import FilewriterCommandWidget


class Ui_FilewriterCtrl(object):
    def setupUi(self, FilewriterCtrl):
        FilewriterCtrl.resize(649, 450)
        FilewriterCtrl.setWindowTitle("File Writer Control Window")
        broker_placeholder_text = "address:port/topic"
        self.central_widget = QWidget(FilewriterCtrl)
        self.vertical_layout_2 = QVBoxLayout(self.central_widget)
        self.vertical_layout = QVBoxLayout()
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.setContentsMargins(-1, -1, 0, -1)
        self.status_layout = QVBoxLayout()
        self.status_layout.setContentsMargins(-1, -1, -1, 0)
        self.status_topic_layout = QHBoxLayout()
        self.status_topic_layout.setContentsMargins(-1, -1, -1, 0)
        self.status_broker_label = QLabel(self.central_widget)
        self.status_topic_layout.addWidget(self.status_broker_label)
        self.status_broker_edit = QLineEdit(self.central_widget)
        self.status_broker_edit.setPlaceholderText(broker_placeholder_text)

        self.status_topic_layout.addWidget(self.status_broker_edit)
        self.status_layout.addLayout(self.status_topic_layout)
        self.line_2 = QFrame(self.central_widget)
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.status_layout.addWidget(self.line_2)
        self.file_writer_table_group = QGroupBox(self.central_widget)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(
            self.file_writer_table_group.sizePolicy().hasHeightForWidth()
        )
        self.file_writer_table_group.setSizePolicy(size_policy)
        self.vertical_layout_4 = QVBoxLayout(self.file_writer_table_group)
        self.vertical_layout_3 = QVBoxLayout()
        self.file_writers_list = QTreeView(self.file_writer_table_group)
        self.file_writers_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.file_writers_list.setIndentation(0)
        self.vertical_layout_3.addWidget(self.file_writers_list)
        self.vertical_layout_4.addLayout(self.vertical_layout_3)
        self.status_layout.addWidget(self.file_writer_table_group)
        self.files_group = QGroupBox(self.central_widget)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(4)
        size_policy.setHeightForWidth(self.files_group.sizePolicy().hasHeightForWidth())
        self.files_group.setSizePolicy(size_policy)
        self.vertical_layout_6 = QVBoxLayout(self.files_group)
        self.files_list = QTreeView(self.files_group)
        self.files_list.setIndentation(0)
        self.vertical_layout_6.addWidget(self.files_list)
        self.vertical_layout_5 = QVBoxLayout()
        self.horizontal_layout_4 = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontal_layout_4.addItem(spacer)
        self.stop_file_writing_button = QPushButton(self.files_group)
        self.stop_file_writing_button.setEnabled(False)
        self.horizontal_layout_4.addWidget(self.stop_file_writing_button)
        self.vertical_layout_5.addLayout(self.horizontal_layout_4)
        self.vertical_layout_6.addLayout(self.vertical_layout_5)
        self.status_layout.addWidget(self.files_group)
        self.horizontal_layout.addLayout(self.status_layout)
        self.line = QFrame(self.central_widget)
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.horizontal_layout.addWidget(self.line)

        self.command_layout = QVBoxLayout()
        self.command_layout.setContentsMargins(-1, 0, -1, 0)
        self.command_broker_layout = QHBoxLayout()
        self.command_broker_label = QLabel(self.central_widget)
        self.command_broker_layout.addWidget(self.command_broker_label)
        self.command_broker_edit = QLineEdit(self.central_widget)
        self.command_broker_edit.setPlaceholderText(broker_placeholder_text)
        self.command_broker_layout.addWidget(self.command_broker_edit)
        self.command_layout.addLayout(self.command_broker_layout)
        self.command_widget = FilewriterCommandWidget(FilewriterCtrl)
        self.command_layout.addWidget(self.command_widget)

        self.horizontal_layout.addLayout(self.command_layout)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout_2.addLayout(self.vertical_layout)
        FilewriterCtrl.setCentralWidget(self.central_widget)

        self.status_broker_label.setText("Status broker")
        self.file_writer_table_group.setTitle("File-writers")
        self.files_group.setTitle("Files")
        self.stop_file_writing_button.setText("Stop file-writing")
        self.command_broker_label.setText("Command broker")
        self.command_broker_edit.setPlaceholderText("address:port/topic")

        QMetaObject.connectSlotsByName(FilewriterCtrl)
