"""
Entry script for the nexus constructor application.
Requires Python 3.6+
"""
import argparse
import logging
import os

os.environ["QT_MAC_WANTS_LAYER"] = "1"
import locale
import signal
import sys

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow

from nexus_constructor.component_type import make_dictionary_of_class_definitions
from nexus_constructor.main_window import MainWindow
from nexus_constructor.model.model import Model

signal.signal(signal.SIGINT, signal.SIG_DFL)

if getattr(sys, "frozen", False):
    # frozen
    root_dir = os.path.dirname(sys.executable)
else:
    root_dir = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    if locale.getlocale()[0] is None:
        used_locale = "en_GB.UTF-8"
        locale.setlocale(locale.LC_ALL, used_locale)
        print(
            f"Unable to determine the system locale, using the default ({used_locale})."
        )
    parser = argparse.ArgumentParser(description="Nexus Constructor")
    if "help" in parser.parse_args():
        exit(0)
    logging.basicConfig(level=logging.INFO)
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join("ui", "icon.png")))
    window = QMainWindow()
    definitions_dir = os.path.abspath(os.path.join(root_dir, "definitions"))
    _, nx_component_classes = make_dictionary_of_class_definitions(definitions_dir)
    model = Model()
    ui = MainWindow(model, nx_component_classes)
    ui.setupUi(window)
    window.showMaximized()
    sys.exit(app.exec_())
