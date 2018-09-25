import sys
from geometry_constructor.Models import PixelModel
from geometry_constructor.Writers import HdfWriter, Logger
from os import path
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl
from PySide2.QtQml import qmlRegisterType


qmlRegisterType(Logger, 'MyWriters', 1, 0, 'Logger')
qmlRegisterType(HdfWriter, 'MyWriters', 1, 0, 'HdfWriter')
qmlRegisterType(PixelModel, 'MyModels', 1, 0, 'PixelModel')


class Window(QQuickView):

    def __init__(self):
        super().__init__()
        url = QUrl.fromLocalFile(path.join(path.dirname(__file__), 'Qt models\main.qml'))
        self.setSource(url)
        if self.status() == QQuickView.Error:
            print(self.errors(), file=sys.stderr)
            sys.exit(-1)
        self.setTitle("Nexus Geometry Test App")
        self.setResizeMode(QQuickView.SizeRootObjectToView)


if __name__ == '__main__':
    sys_argv = sys.argv + ['--style', 'Material']

    app = QApplication(sys_argv)
    view = Window()
    view.show()
    res = app.exec_()
    del view
    sys.exit(res)
