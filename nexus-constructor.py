"""
Entry script for the nexus constructor application.
"""
import argparse
import logging
import os
import signal
import sys

from PySide6 import QtCore
from PySide6.QtGui import QCloseEvent, QIcon, QSurfaceFormat
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from nexus_constructor.component_type import make_dictionary_of_class_definitions
from nexus_constructor.main_window import MainWindow
from nexus_constructor.model.model import Model

signal.signal(signal.SIGINT, signal.SIG_DFL)

if getattr(sys, "frozen", False):
    # frozen
    root_dir = os.path.dirname(sys.executable)
else:
    root_dir = os.path.dirname(os.path.realpath(__file__))


X_LOC = "window_x_location"
Y_LOC = "window_y_location"
X_SIZE = "window_x_size"
Y_SIZE = "window_y_size"


class NexusConstructorMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._config = QtCore.QSettings("ESS", "nexus-constructor")

    def show(self):
        first_run = not self._config.contains(X_SIZE)
        if first_run:
            self.showMaximized()
        else:
            self.resize(
                int(self._config.value(X_SIZE, 500)),
                int(self._config.value(Y_SIZE, 500)),
            )
            self.move(
                int(self._config.value(X_LOC, 0)), int(self._config.value(Y_LOC, 0))
            )
            super().show()

    def closeEvent(self, event: QCloseEvent) -> None:
        msg = QMessageBox.question(
            None,
            "Close application",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if msg == QMessageBox.Yes:
            window_size = self.size()
            self._config.setValue(X_SIZE, window_size.width())
            self._config.setValue(Y_SIZE, window_size.height())
            window_loc = self.pos()
            self._config.setValue(X_LOC, window_loc.x())
            self._config.setValue(Y_LOC, window_loc.y())
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.c()))
    parser = argparse.ArgumentParser(description="Nexus Constructor")
    if "help" in parser.parse_args():
        exit(0)
    logging.basicConfig(level=logging.INFO)
    if sys.platform == "darwin":
        QApplication.setStyle(
            "Fusion"
        )  # this helps macOS but causes Linux GUI to be unusable
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    surfaceFormat = QSurfaceFormat()
    surfaceFormat.setSwapInterval(1)
    surfaceFormat.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
    QSurfaceFormat.setDefaultFormat(surfaceFormat)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join("ui", "icon.png")))
    window = NexusConstructorMainWindow()
    definitions_dir = os.path.abspath(os.path.join(root_dir, "definitions"))
    _, nx_component_classes = make_dictionary_of_class_definitions(definitions_dir)
    model = Model()
    ui = MainWindow(model, nx_component_classes)
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
