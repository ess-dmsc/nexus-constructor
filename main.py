import sys
from os import path, environ
from geometry_constructor.Application import Application
from geometry_constructor.Models import InstrumentModel
from geometry_constructor.Writers import HdfWriter, Logger
from PySide2.QtCore import QUrl, QObject
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import qmlRegisterType


qmlRegisterType(Logger, 'MyWriters', 1, 0, 'Logger')
qmlRegisterType(HdfWriter, 'MyWriters', 1, 0, 'HdfWriter')
qmlRegisterType(InstrumentModel, 'MyModels', 1, 0, 'InstrumentModel')

location = sys.executable if getattr(sys, 'frozen', False) else __file__
resource_folder = path.join(path.dirname(location), 'resources')

environ['QT_QUICK_CONTROLS_CONF'] = path.join(resource_folder, 'qtquickcontrols2.conf')


# Stop the application if Qt is unable to load the UI from qml
# By default errors should be logged http://doc.qt.io/qt-5/qqmlapplicationengine.html#load
# but these will not stop the application from running without a UI, and don't appear in the PyCharm console
def load_listener(loaded_object: QObject, target_url: QUrl):
    if loaded_object is None:
        print("Unable to load from url: {0}\nExiting".format(target_url.toString()), file=sys.stderr)
        sys.exit(-1)


app = QGuiApplication(sys.argv)

window = Application(resource_folder)

res = app.exec_()
sys.exit(res)
