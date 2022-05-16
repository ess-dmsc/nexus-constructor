from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from nexus_constructor.model.writer_module_container import ModuleContainer  # type: ignore
from .positive_integer_setting import PositiveIntegerSetting


class ChunkCueEdit(QWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent)
        self._container = container
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(QLabel(parent=self, text="Chunk size"))
        self._chunk_size_edit = PositiveIntegerSetting(self, container, "chunk_size")
        self.layout().addWidget(self._chunk_size_edit)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(line)

        self.layout().addWidget(QLabel(parent=self, text="Cue interval"))
        self._cue_interval_edit = PositiveIntegerSetting(
            self, container, "cue_interval"
        )
        self.layout().addWidget(self._cue_interval_edit)
