from PySide2.QtCore import Qt, QSize, QPoint, QModelIndex, QAbstractItemModel, QObject
from PySide2.QtWidgets import (
    QStyledItemDelegate,
    QFrame,
    QVBoxLayout,
    QSizePolicy,
    QLabel,
    QStyleOptionViewItem,
    QWidget,
)
from nexus_constructor.component_tree_model import ComponentInfo, LinkTransformation
from nexus_constructor.component.component import Component, TransformationsList
from nexus_constructor.transformation_types import TransformationType
from nexus_constructor.transformations import Transformation
from nexus_constructor.instrument import Instrument
from PySide2.QtGui import QPixmap, QRegion, QPainter, QColor
from nexus_constructor.transformation_view import (
    EditTranslation,
    EditRotation,
    EditTransformationLink,
)

from typing import Union


class ComponentEditorDelegate(QStyledItemDelegate):
    frameSize = QSize(30, 10)

    def __init__(self, parent: QObject, instrument: Instrument):
        super().__init__(parent)
        self.instrument = instrument

    def getFrame(
        self,
        value: Union[
            Component,
            ComponentInfo,
            Transformation,
            LinkTransformation,
            TransformationsList,
        ],
    ):
        frame = QFrame()
        frame.setAutoFillBackground(True)
        SizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        SizePolicy.setHorizontalStretch(0)
        SizePolicy.setVerticalStretch(0)

        AltSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        AltSizePolicy.setVerticalStretch(0)

        frame.setSizePolicy(SizePolicy)
        frame.layout = QVBoxLayout()
        frame.layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(frame.layout)
        if isinstance(value, Component):
            frame.label = QLabel(f"{value.name} ({value.nx_class})", frame)
            frame.layout.addWidget(frame.label)
        elif isinstance(value, TransformationsList):
            frame.label = QLabel("Transformations", frame)
            frame.layout.addWidget(frame.label)
        elif isinstance(value, ComponentInfo):
            frame.label = QLabel("(Place holder)", frame)
            frame.layout.addWidget(frame.label)
        elif isinstance(value, Transformation):
            if value.type == TransformationType.TRANSLATION.value:
                frame.transformation_frame = EditTranslation(
                    frame, value, self.instrument
                )
            elif value.type == TransformationType.ROTATION.value:
                frame.transformation_frame = EditRotation(frame, value, self.instrument)
            else:
                raise (
                    RuntimeError(
                        'Transformation type "{}" is unknown.'.format(value.type)
                    )
                )
            frame.layout.addWidget(frame.transformation_frame, Qt.AlignTop)
        elif isinstance(value, LinkTransformation):
            frame.transformation_frame = EditTransformationLink(
                frame, value, self.instrument
            )
            frame.layout.addWidget(frame.transformation_frame, Qt.AlignTop)
        return frame

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ):
        model = index.model()
        value = model.data(index, Qt.DisplayRole)
        frame = self.getFrame(value)
        frame.setFixedSize(option.rect.size())
        ratio = self.parent().devicePixelRatioF()
        pixmap = QPixmap(frame.size() * ratio)
        pixmap.setDevicePixelRatio(ratio)
        frame.render(pixmap, QPoint(), QRegion())
        painter.drawPixmap(option.rect, pixmap)
        if index in self.parent().selectedIndexes():
            colour = QColor("lightblue")
            colour.setAlpha(100)
            painter.fillRect(option.rect, colour)

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QWidget:
        model = index.model()
        value = model.data(index, Qt.DisplayRole)
        frame = self.getFrame(value)
        frame.transformation_frame.enable()
        frame.setParent(parent)
        self.frameSize = frame.sizeHint()
        return frame

    def setModelData(
        self, editorWidget: QWidget, model: QAbstractItemModel, index: QModelIndex
    ):
        editorWidget.transformation_frame.saveChanges()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        model = index.model()
        value = model.data(index, Qt.DisplayRole)
        frame = self.getFrame(value)
        return frame.sizeHint()

    def updateEditorGeometry(
        self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ):
        editor.setGeometry(option.rect)
