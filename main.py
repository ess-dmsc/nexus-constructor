"""
Entry script for the nexus constructor application.
Requires Python 3.6+
"""
import logging
import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2 import QtCore
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.instrument import Instrument

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setWindowIcon(QIcon("ui/icon.png"))
    window = QMainWindow()
    nexus_wrapper = NexusWrapper()
    instrument = Instrument(nexus_wrapper)
    ui = MainWindow(instrument)
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
