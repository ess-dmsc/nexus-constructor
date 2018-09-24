import sys
from Writers import HdfWriter, Logger
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl
from PySide2.QtQml import qmlRegisterType


app = QApplication([])
qmlRegisterType(Logger, 'MyWriters', 1, 0, 'Logger')
qmlRegisterType(HdfWriter, 'MyWriters', 1, 0, 'HdfWriter')
view = QQuickView()
url = QUrl("Qt models/main.qml")

view.setSource(url)
if view.status() == QQuickView.Error:
    print(view.errors(), file=sys.stderr)
    sys.exit(-1)
view.setTitle("Nexus Geometry Test App")
view.setResizeMode(QQuickView.SizeRootObjectToView)
view.show()
res = app.exec_()
del view
sys.exit(res)
