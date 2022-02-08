import sys
import time

from PySide2 import QtCore
from PySide2.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        central_widget = QWidget()
        layout = QHBoxLayout()
        button = QPushButton("Start long task")
        layout.addWidget(button)
        button.clicked.connect(self.test)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def test(self):
        with StatusDialog(time.sleep, args=(4,), parent=self) as _:
            print("Done!!")
        # time.sleep(2)


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


class StatusDialog(QDialog):
    def __init__(self, operation, args=(), parent=None) -> None:
        super().__init__(parent)
        self.operation = operation
        self.args = args

        layout = QVBoxLayout()
        self.progress_bar = ProgressBar(self, minimum=0, maximum=0)

        self.task = LongRunningTask(operation, args)
        self.task.finished.connect(self.slot_done)

        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def slot_done(self):
        self.accept()

    def __enter__(self):
        self.open()
        self.task.start()
        return self

    def __exit__(self, type, value, traceback):
        pass


class LongRunningTask(QtCore.QThread):
    finished = QtCore.Signal()

    def __init__(self, operation, args=(), parent=None) -> None:
        super().__init__(parent)
        self.operation = operation
        self.args = args

    def run(self):
        self.operation(*self.args)
        self.finished.emit()


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
