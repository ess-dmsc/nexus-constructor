#!/usr/bin/env python

from PySide2.QtCore import Qt, QSize, QPoint
from PySide2.QtWidgets import QApplication, QTreeView, QHBoxLayout, QStyledItemDelegate, QFrame, QGroupBox, QPushButton, QVBoxLayout, QSizePolicy, QLabel, QLineEdit
from nexus_constructor.component_tree_model import ComponentInfo
from nexus_constructor.component import ComponentModel
from nexus_constructor.transformations import TransformationModel, TransformationsList
from PySide2.QtGui import QPixmap, QRegion
import PySide2.QtGui
from nexus_constructor.transformation_view import EditTranslation

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
        if isinstance(value, ComponentModel):
            frame.label = QLabel("{} ({})".format(value.name, value.nx_class), frame)
            frame.layout.addWidget(frame.label)
        elif isinstance(value, TransformationsList):
            frame.label = QLabel("Transformations", frame)
            frame.layout.addWidget(frame.label)
        elif isinstance(value, ComponentInfo):
            frame.label = QLabel("Component settings", frame)
            frame.layout.addWidget(frame.label)
        elif isinstance(value, TransformationModel):
            if value.type == "Translation":
                pass
            elif value.type == "Rotation":
                pass
            else:
                raise NotImplementedError("Unknown transformation type.")
            frame.transformation_frame = EditTranslation(frame, value)
            frame.layout.addWidget(frame.transformation_frame, Qt.AlignTop)

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
        editorWidget.setEnabled(True)

    def setModelData(self, editorWidget, model, index):
        editorWidget.setEnabled(False)

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
