"""
Contains the main class for the nexus geometry constructor

Loading this module also registers with QML the required custom classes to load the application's QML GUI
"""

import sys
from os import path
from geometry_constructor.instrument_model import InstrumentModel
from geometry_constructor.geometry_models import CylinderModel, OFFModel
from geometry_constructor.json_loader import JsonLoader
from geometry_constructor.json_writer import JsonWriter
from geometry_constructor.qml_json_model import FilteredJsonModel
from geometry_constructor.writers import HdfWriter, Logger
from PySide2.QtCore import QUrl, QObject
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType


qmlRegisterType(Logger, 'MyWriters', 1, 0, 'Logger')
qmlRegisterType(HdfWriter, 'MyWriters', 1, 0, 'HdfWriter')
qmlRegisterType(InstrumentModel, 'MyModels', 1, 0, 'InstrumentModel')
qmlRegisterType(CylinderModel, 'MyModels', 1, 0, 'CylinderModel')
qmlRegisterType(OFFModel, 'MyModels', 1, 0, 'OFFModel')
qmlRegisterType(FilteredJsonModel, 'MyModels', 1, 0, 'FilteredJsonModel')
qmlRegisterType(JsonLoader, 'MyJson', 1, 0, 'JsonLoader')
qmlRegisterType(JsonWriter, 'MyJson', 1, 0, 'JsonWriter')


class Application(QQmlApplicationEngine):
    """Main gui class for the nexus geometry constructor"""

    def __init__(self, resource_folder):
        super().__init__()

        # Stop the application if Qt is unable to load the UI from qml
        # By default errors should be logged http://doc.qt.io/qt-5/qqmlapplicationengine.html#load
        # but these will not stop the application from running without a UI, and don't appear in the PyCharm console
        def load_listener(loaded_object: QObject, target_url: QUrl):
            if loaded_object is None:
                print("Unable to load from url: {0}\nExiting".format(target_url.toString()), file=sys.stderr)
                sys.exit(-1)

        url = QUrl.fromLocalFile(path.join(resource_folder, 'Qt models', 'Main.qml'))
        self.objectCreated.connect(load_listener)
        self.load(url)
