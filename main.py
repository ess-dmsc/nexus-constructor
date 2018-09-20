import sys
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl

app = QApplication([])
view = QQuickView()
url = QUrl("Qt models/main.qml")

view.setSource(url)
if view.status() == QQuickView.Error:
    print(view.errors(), file=sys.stderr)
    sys.exit(-1)
view.setResizeMode(QQuickView.SizeRootObjectToView)
view.show()
res = app.exec_()
del view
sys.exit(res)
