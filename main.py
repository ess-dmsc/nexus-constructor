"""
Entry script for the nexus constructor application.
Requires Python 3.6+
"""

import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2 import QtCore
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus_wrapper import NexusWrapper

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setWindowIcon(QIcon("ui/icon.png"))
    window = QMainWindow()
    nexus_wrapper = NexusWrapper()
    ui = MainWindow(nexus_wrapper)
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
