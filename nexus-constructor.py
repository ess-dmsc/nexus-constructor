"""
Entry script for the nexus constructor application.
Requires Python 3.6+
"""
import logging
import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2 import QtCore

from nexus_constructor.component.component_type import (
    make_dictionary_of_class_definitions,
)
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.instrument import Instrument
import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nexus Constructor")
    if "help" in parser.parse_args():
        exit(0)
    logging.basicConfig(level=logging.INFO)
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join("ui", "icon.png")))
    window = QMainWindow()
    nexus_wrapper = NexusWrapper()
    definitions_dir = os.path.abspath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "definitions")
    )
    _, nx_component_classes = make_dictionary_of_class_definitions(definitions_dir)
    instrument = Instrument(nexus_wrapper, nx_component_classes)
    ui = MainWindow(instrument, nx_component_classes)
    ui.setupUi(window)
    window.showMaximized()
    sys.exit(app.exec_())
