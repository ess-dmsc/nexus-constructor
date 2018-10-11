import sys
from os import path, environ
from geometry_constructor.Application import Application
from geometry_constructor.QmlModel import InstrumentModel
from geometry_constructor.Writers import HdfWriter, Logger
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import qmlRegisterType


qmlRegisterType(Logger, 'MyWriters', 1, 0, 'Logger')
qmlRegisterType(HdfWriter, 'MyWriters', 1, 0, 'HdfWriter')
qmlRegisterType(InstrumentModel, 'MyModels', 1, 0, 'InstrumentModel')

location = sys.executable if getattr(sys, 'frozen', False) else __file__
resource_folder = path.join(path.dirname(location), 'resources')

environ['QT_QUICK_CONTROLS_CONF'] = path.join(resource_folder, 'qtquickcontrols2.conf')

app = QGuiApplication(sys.argv)

window = Application(resource_folder)

res = app.exec_()
sys.exit(res)
