import sys
from os import path
from geometry_constructor.instrument_model import InstrumentModel
from geometry_constructor.writers import HdfWriter, Logger
from PySide2.QtCore import QUrl, QObject
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType


qmlRegisterType(Logger, 'MyWriters', 1, 0, 'Logger')
qmlRegisterType(HdfWriter, 'MyWriters', 1, 0, 'HdfWriter')
qmlRegisterType(InstrumentModel, 'MyModels', 1, 0, 'InstrumentModel')


class Application(QQmlApplicationEngine):

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
