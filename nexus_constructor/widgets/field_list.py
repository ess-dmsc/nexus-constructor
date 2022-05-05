from PySide2.QtWidgets import QListView, QWidget, QLabel, QStyledItemDelegate, QFrame, QSizePolicy, QStyleOptionViewItem, QVBoxLayout, QAbstractItemView
from PySide2.QtCore import QAbstractListModel, QModelIndex, Signal, Qt, QPoint, QSize
from PySide2.QtGui import QPainter, QPixmap, QRegion
from nexus_constructor.model import GroupContainer, Group, Dataset
import PySide2
import typing
from typing import Dict, Optional
from nexus_constructor.widgets.field_item import FieldItem
from nexus_constructor.validators import MultiItemValidator
from functools import partial


class FieldListModel(QAbstractListModel):
    def __init__(self, parent: QWidget, group_container: GroupContainer):
        super().__init__(parent)
        self._group_container = group_container

    def fieldItems(self):
        return [item for item in self._group_container.group.children if not isinstance(item, Group)]

    def rowCount(self, parent: PySide2.QtCore.QModelIndex = QModelIndex()) -> int:
        return len(self.fieldItems())

    def data(self, index: PySide2.QtCore.QModelIndex, role=QModelIndex()) -> typing.Any:
        if not index.isValid():
            return None
        if index.row() >= self.rowCount(None) or index.row() < 0:
            return None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.fieldItems()[index.row()]
        return None

    def flags(self, index:PySide2.QtCore.QModelIndex) -> PySide2.QtCore.Qt.ItemFlags:
        return Qt.ItemIsEnabled | Qt.ItemIsEditable


class FieldItemDelegate(QStyledItemDelegate):
    frameSize = QSize(30, 10)

    def __init__(self, parent, validator: MultiItemValidator):
        super().__init__(parent)
        self._validator = validator
        self._dict_frames: Dict[QModelIndex, QFrame] = {}

    def get_frame(self, index: QModelIndex, parent: Optional[QWidget] = None):
        if parent is None:
            parent = self.parent()
        c_module = index.model().data(index, Qt.DisplayRole)
        frame = FieldItem(parent=parent, file_writer_module=c_module)
        frame.is_valid.connect(partial(self._validator.set_is_valid, c_module))
        frame.is_valid.emit(None)
        frame.setAutoFillBackground(True)
        SizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        SizePolicy.setHorizontalStretch(0)
        SizePolicy.setVerticalStretch(0)
        frame.setSizePolicy(SizePolicy)
        frame.setLayout(QVBoxLayout())
        frame.layout().setContentsMargins(0, 0, 0, 0)
        return frame

    def createEditor(self, parent: PySide2.QtWidgets.QWidget, option: PySide2.QtWidgets.QStyleOptionViewItem, index: PySide2.QtCore.QModelIndex) -> PySide2.QtWidgets.QWidget:
        frame = self.get_frame(index, parent=parent)
        self.frameSize = frame.sizeHint()
        return frame

    def updateEditorGeometry(self, editor: PySide2.QtWidgets.QWidget, option: PySide2.QtWidgets.QStyleOptionViewItem, index: PySide2.QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        frame = self.get_frame(index)
        frame.setFixedSize(option.rect.size())
        ratio = self.parent().devicePixelRatioF()
        pixmap = QPixmap(frame.size() * ratio)
        pixmap.setDevicePixelRatio(ratio)
        frame.render(pixmap, QPoint(), QRegion())
        painter.drawPixmap(option.rect, pixmap)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        frame = self.get_frame(index)
        return frame.sizeHint()


class FileListModel(QAbstractListModel):
    numberPopulated = Signal(int)

    def __init__(self, parent=None):
        super(FileListModel, self).__init__(parent)

        self.fileCount = 2
        self.fileList = ["File1", "File2"]

    def rowCount(self, parent=QModelIndex()):
        return self.fileCount

    def flags(self, index: PySide2.QtCore.QModelIndex) -> PySide2.QtCore.Qt.ItemFlags:
        return Qt.ItemIsEnabled | Qt.ItemIsEditable

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() >= len(self.fileList) or index.row() < 0:
            return None

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return_val = QLabel(parent=self.parent())
            return_val.setText(self.fileList[index.row()])
            return self.fileList[index.row()]
        return None


class FieldList(QListView):
    def __init__(self, parent: QWidget, group_container: GroupContainer):
        super().__init__(parent)
        self._group_container = group_container
        self._field_validator = MultiItemValidator()
        self._field_validator.is_valid.connect(self.handle_validity_signal)
        self._model = FieldListModel(self, group_container)
        self._item_delegate = FieldItemDelegate(parent, self._field_validator)
        self.setItemDelegate(self._item_delegate)
        self.setModel(self._model)
        self.setEditTriggers(QAbstractItemView.AllEditTriggers)

    def handle_validity_signal(self, valid: bool):
        self._purge_removed_validator_items()
        self.is_valid.emit(self._field_validator.known_items_are_valid())

    def _purge_removed_validator_items(self):
        known_items = list(self._field_validator.items)
        for item in known_items:
            if item not in self._group_container.group.children:
                self._field_validator.remove_item(item, no_emit=True)

    def add_field(self):
        self._model.beginInsertRows(QModelIndex(), self._model.rowCount(), self._model.rowCount())
        c_group = self._group_container.group
        new_dataset = Dataset(parent_node=c_group, name="", values=0, type="double")
        c_group.children.append(new_dataset)
        self._model.endInsertRows()

    def remove_selected_field(self):
        c_index = self.currentIndex()
        self._model.beginRemoveRows(QModelIndex(), c_index.row(), c_index.row())
        c_field_parent = c_index.data().parent_node
        c_field_parent.children.remove(c_index.data())
        self._model.endRemoveRows()
        self._field_validator.remove_item(c_index.data())

    is_valid = Signal(bool)

