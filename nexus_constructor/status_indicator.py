from functools import wraps

from PySide2 import QtCore
from PySide2.QtWidgets import QDialog, QProgressBar, QVBoxLayout


class ProgressBar(QProgressBar):
    PROGRESS_BAR_STYLE_SHEET = """
        QProgressBar {
            min-height: 12px;
            max-height: 12px;
            border-radius: 6px;
        }
        QProgressBar::chunk {
            border-radius: 6px;
            background-color: #009688;
        }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(self.PROGRESS_BAR_STYLE_SHEET)
        self.setValue(0)


def status_indicator():
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            class _TaskThread(QtCore.QThread):
                finished = QtCore.Signal()

                def __init__(self, operation, *args, **kwargs) -> None:
                    super().__init__(parent)
                    self.operation = operation
                    self.args = args
                    self.kwargs = kwargs

                def run(self):
                    self.operation(*self.args, **kwargs)
                    self.finished.emit()

            class _StatusDialog(QDialog):
                def __init__(self, parent, operation, *args, **kwargs) -> None:
                    super().__init__(parent)
                    self.initUi()
                    self.task = _TaskThread(operation, *args, **kwargs)
                    self.task.finished.connect(self._on_task_finished)
                    self.task.start()

                def initUi(self):
                    layout = QVBoxLayout()
                    progress_bar = ProgressBar(self, minimum=0, maximum=0)
                    layout.addWidget(progress_bar)
                    self.setLayout(layout)

                def _on_task_finished(self):
                    self.accept()

                def closeEvent(self, QCloseEvent):
                    self.task.terminate()
                    self.task.wait()
                    super().closeEvent(QCloseEvent)

            parent = args[0]
            status = _StatusDialog(parent, func, *args, **kwargs)
            status.open()

        return inner

    return wrapper
