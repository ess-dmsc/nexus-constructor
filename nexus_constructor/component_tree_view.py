from typing import Union

from PySide2.QtCore import QAbstractItemModel, QModelIndex, QObject, QPoint, QSize, Qt
from PySide2.QtGui import QPainter, QPixmap, QRegion
from PySide2.QtWidgets import (
    QFrame,
    QSizePolicy,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from nexus_constructor.component_tree_model import ComponentInfo, LinkTransformation
from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import FileWriterModule
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.transformations_list import TransformationsList
from nexus_constructor.treeview_utils import (
    fill_selection,
    get_group_frame,
    get_group_info_frame,
    get_link_transformation_frame,
    get_module_frame,
    get_transformation_frame,
    get_transformations_list_frame,
)

MODULE_FRAME = "module_frame"
TRANSFORMATION_FRAME = "transformation_frame"


class ComponentEditorDelegate(QStyledItemDelegate):
    frameSize = QSize(30, 10)

    def __init__(self, parent: QObject, model: Model):
        super().__init__(parent)
        self.model = model
        self._use_simple_tree_view = False

    def get_frame(
        self,
        value: Union[
            Component,
            ComponentInfo,
            Transformation,
            LinkTransformation,
            TransformationsList,
            FileWriterModule,
        ],
    ):
        frame = QFrame()
        frame.setAutoFillBackground(True)
        SizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        SizePolicy.setHorizontalStretch(0)
        SizePolicy.setVerticalStretch(0)
        frame.setSizePolicy(SizePolicy)
        frame.setLayout(QVBoxLayout())
        frame.layout().setContentsMargins(0, 0, 0, 0)

        if isinstance(value, Group):
            get_group_frame(frame, value)
        elif isinstance(value, TransformationsList):
            get_transformations_list_frame(frame)
        elif isinstance(value, ComponentInfo):
            get_group_info_frame(frame, value)
        elif isinstance(value, Transformation):
            get_transformation_frame(frame, self.model, value)
        elif isinstance(value, LinkTransformation):
            get_link_transformation_frame(frame, self.model, value)
        elif isinstance(value, FileWriterModule):
            get_module_frame(frame, self.model, value, self._use_simple_tree_view)
        return frame

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ):
        model = index.model()
        value = model.data(index, Qt.DisplayRole)
        frame = self.get_frame(value)
        frame.setFixedSize(option.rect.size())
        ratio = self.parent().devicePixelRatioF()
        pixmap = QPixmap(frame.size() * ratio)
        pixmap.setDevicePixelRatio(ratio)
        frame.render(pixmap, QPoint(), QRegion())
        painter.drawPixmap(option.rect, pixmap)
        if index in self.parent().selectedIndexes():
            fill_selection(option, painter)

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QWidget:
        model = index.model()
        value = model.data(index, Qt.DisplayRole)
        frame = self.get_frame(value)
        if hasattr(frame, TRANSFORMATION_FRAME):
            frame.transformation_frame.enable()
        frame.setParent(parent)
        self.frameSize = frame.sizeHint()
        return frame

    def setModelData(
        self, editorWidget: QWidget, model: QAbstractItemModel, index: QModelIndex
    ):
        if hasattr(editorWidget, TRANSFORMATION_FRAME):
            editorWidget.transformation_frame.save_all_changes()
        elif hasattr(editorWidget, MODULE_FRAME):
            editorWidget.module_frame.save_module_changes()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        model = index.model()
        value = model.data(index, Qt.DisplayRole)
        frame = self.get_frame(value)
        return frame.sizeHint()

    def updateEditorGeometry(
        self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ):
        editor.setGeometry(option.rect)

    def use_simple_tree_view(self, use_simple_view):
        self._use_simple_tree_view = use_simple_view
