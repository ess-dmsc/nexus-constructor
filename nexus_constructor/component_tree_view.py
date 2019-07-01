#!/usr/bin/env python

from PySide2.QtCore import Qt, QSize, QPoint
from PySide2.QtWidgets import QApplication, QTreeView, QHBoxLayout, QStyledItemDelegate, QFrame, QPushButton, QVBoxLayout, QSizePolicy, QLabel, QLineEdit
from nexus_constructor.component_tree_model import ComponentInfo
from nexus_constructor.component import ComponentModel
from nexus_constructor.transformations import TransformationModel, TransformationsList
from PySide2.QtGui import QPixmap, QRegion
import PySide2.QtGui
# from ui.transformations import Ui_TransformationFrame

class ComponentEditorDelegate(QStyledItemDelegate):
    SettingsFrameMap = {} #{Rotation:RotateSettingsFrame, Translation:TranslateSettingsFrame}
    frameSize = QSize(30, 10)

    def __init__(self, parent):
        super().__init__(parent)

    def getFrame(self, value):
        frame = QFrame()
        frame.setAutoFillBackground(True)
        SizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        SizePolicy.setHorizontalStretch(0)
        SizePolicy.setVerticalStretch(0)

        AltSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        AltSizePolicy.setVerticalStretch(0)

        frame.setSizePolicy(SizePolicy)
        frame.layout = QVBoxLayout()
        frame.layout.setContentsMargins(0,0,0,0)
        frame.setLayout(frame.layout)
        if issubclass(type(value), ComponentModel):
            frame.label = QLabel("{} ({})".format(value.name, value.nx_class), frame)
            frame.layout.addWidget(frame.label)
        elif type(value) is TransformationsList:
            frame.label = QLabel("Transformations", frame)
            frame.layout.addWidget(frame.label)
        elif type(value) is ComponentInfo:
            frame.label = QLabel("Component settings", frame)
            frame.layout.addWidget(frame.label)
        elif issubclass(type(value), TransformationModel):
            pass
            # frame.transformation_frame = Ui_TransformationFrame()
            # temp_frame = QFrame(frame)
            # frame.transformation_frame.setupUi(temp_frame)
            # frame.layout.addWidget(temp_frame, Qt.AlignTop)
        #     frame.editor_header_layout = QHBoxLayout()
        #     label = QLabel("Name", frame)
        #     label.setSizePolicy(SizePolicy)
        #     frame.editor_header_layout.addWidget(label)
        #     frame.editor_header_layout.setContentsMargins(0, 0, 0, 0)
        #     frame.component_name = QLineEdit(value.Name, frame)
        #     frame.component_name.setSizePolicy(AltSizePolicy)
        #     line = QFrame(frame)
        #     line.setFrameShape(QFrame.VLine)
        #     line.setFrameShadow(QFrame.Sunken)
        #     frame.editor_header_layout.addWidget(frame.component_name)
        #     frame.editor_header_layout.addWidget(line)
        #     frame.edit_btn = QPushButton("Edit", frame)
        #     frame.edit_btn.setSizePolicy(SizePolicy)
        #     frame.editor_header_layout.addWidget(frame.edit_btn)
        #     frame.layout.addLayout(frame.editor_header_layout)
        #     frame.editor_header_layout.setEnabled(False)
        #     line2 = QFrame(frame)
        #     line2.setFrameShape(QFrame.HLine)
        #     line2.setFrameShadow(QFrame.Sunken)
        #     line2.setContentsMargins(0, 0, 0, 0)
        #     frame.setContentsMargins(0, 0, 0, 0)
        #     frame.layout.setContentsMargins(0, 0, 0, 0)
        #     frame.layout.addWidget(line2)
        #     frame.edit_frame = self.SettingsFrameMap[type(value)](value, frame)
        #     frame.layout.addWidget(frame.edit_frame, Qt.AlignTop)
        #     frame.edit_frame.setEnabled(False)
        #     frame.component_name.setEnabled(False)
        # else:
        #     raise Exception("Unknown element type in tree view.")

        return frame

    def paint(self, painter, option, index):
        model = index.model()
        value = model.data(index, Qt.DisplayRole)
        frame = self.getFrame(value)
        frame.setFixedSize(option.rect.size())
        ratio = self.parent().devicePixelRatioF()
        pixmap = QPixmap(frame.size() * ratio)
        pixmap.setDevicePixelRatio(ratio)
        frame.render(pixmap, QPoint(), QRegion())
        painter.drawPixmap(option.rect, pixmap)

    def createEditor(self, parent, option, index):
        model = index.model()
        value = model.data(index, Qt.DisplayRole)
        frame = self.getFrame(value)
        frame.setParent(parent)
        self.frameSize = frame.sizeHint()
        return frame

    def setEditorData(self, editorWidget, index):
        model = index.model()
        editorWidget.edit_frame.setEnabled(True)
        editorWidget.component_name.setEnabled(True)
        editorWidget.edit_btn.setText("Done")
        #spinBox.editor.setText(value["data"].Name)

    def setModelData(self, editorWidget, model, index):
        editorWidget.edit_frame.setEnabled(False)
        editorWidget.component_name.setEnabled(False)
        editorWidget.edit_btn.setText("Edit")

    def sizeHint(self, option, index):
        model = index.model()
        value = model.data(index, Qt.DisplayRole)
        frame = self.getFrame(value)
        return frame.sizeHint()

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class ComponentTreeView(QTreeView):
    def __init__(self, parent = None):
        super().__init__(parent)

    def dragMoveEvent(self, event):
        print("dragMoveEvent")
        event.setDropAction(Qt.MoveAction)
        event.accept()

    def dragLeaveEvent(self, event: PySide2.QtGui.QDragLeaveEvent):
        print("dragLeaveEvent")

    def dragEnterEvent(self, event: PySide2.QtGui.QDragEnterEvent):
        print("dragEnterEvent")
