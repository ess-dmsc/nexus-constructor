"""
Contains the main class for the nexus constructor

Loading this module also registers with QML the required custom classes to load the application's QML GUI
"""

import sys
from os import path
from nexus_constructor.json_connector import JsonConnector
from nexus_constructor.qml_models.component_filters import SingleComponentModel, ExcludedComponentModel
from nexus_constructor.qml_models.geometry_models import CylinderModel, OFFModel, NoShapeModel
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from nexus_constructor.qml_models.json_model import FilteredJsonModel
from nexus_constructor.qml_models.pixel_models import PixelGridModel, PixelMappingModel, SinglePixelModel
from nexus_constructor.qml_models.transform_model import TransformationModel
from nexus_constructor.validators import NameValidator, TransformParentValidator, NullableIntValidator
from nexus_constructor.writers import HdfWriter, Logger
from PySide2.QtCore import QUrl, QObject
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType


qmlRegisterType(Logger, 'MyWriters', 1, 0, 'Logger')
qmlRegisterType(HdfWriter, 'MyWriters', 1, 0, 'HdfWriter')

qmlRegisterType(InstrumentModel, 'MyModels', 1, 0, 'InstrumentModel')
qmlRegisterType(SingleComponentModel, 'MyModels', 1, 0, 'SingleComponentModel')
qmlRegisterType(ExcludedComponentModel, 'MyModels', 1, 0, 'ExcludedComponentModel')
qmlRegisterType(CylinderModel, 'MyModels', 1, 0, 'CylinderModel')
qmlRegisterType(OFFModel, 'MyModels', 1, 0, 'OFFModel')
qmlRegisterType(NoShapeModel, 'MyModels', 1, 0, 'NoShapeModel')
qmlRegisterType(FilteredJsonModel, 'MyModels', 1, 0, 'FilteredJsonModel')
qmlRegisterType(PixelGridModel, 'MyModels', 1, 0, 'PixelGridModel')
qmlRegisterType(PixelMappingModel, 'MyModels', 1, 0, 'PixelMappingModel')
qmlRegisterType(SinglePixelModel, 'MyModels', 1, 0, 'SinglePixelModel')
qmlRegisterType(TransformationModel, 'MyModels', 1, 0, 'TransformationModel')

qmlRegisterType(JsonConnector, 'MyJson', 1, 0, 'JsonConnector')

qmlRegisterType(NameValidator, 'MyValidators', 1, 0, 'NameValidator')
qmlRegisterType(NullableIntValidator, 'MyValidators', 1, 0, 'NullableIntValidator')
qmlRegisterType(TransformParentValidator, 'MyValidators', 1, 0, 'ParentValidator')


class Application(QQmlApplicationEngine):
    """Main gui class for the nexus constructor"""

    def __init__(self, resource_folder):
        super().__init__()

        # Stop the application if Qt is unable to load the UI from qml
        # By default errors should be logged http://doc.qt.io/qt-5/qqmlapplicationengine.html#load
        # but these will not stop the application from running without a UI, and don't appear in the PyCharm console
        def load_listener(loaded_object: QObject, target_url: QUrl):
            if loaded_object is None:
                print("Unable to load from url: {0}\nExiting".format(target_url.toString()), file=sys.stderr)
                sys.exit(-1)

        url = QUrl.fromLocalFile(path.join(resource_folder, 'QtModels', 'Main.qml'))
        self.objectCreated.connect(load_listener)
        self.load(url)
