import sys
from geometry_constructor.Models import PixelModel
from geometry_constructor.Writers import HdfWriter, Logger
from os import path
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl
from PySide2.QtQml import qmlRegisterType


qmlRegisterType(Logger, 'MyWriters', 1, 0, 'Logger')
qmlRegisterType(HdfWriter, 'MyWriters', 1, 0, 'HdfWriter')
qmlRegisterType(PixelModel, 'MyModels', 1, 0, 'PixelModel')


class Window(QQuickView):

    def __init__(self, resource_folder):
        super().__init__()
        url = QUrl.fromLocalFile(path.join(resource_folder, 'Qt models', 'main.qml'))
        self.setSource(url)
        if self.status() == QQuickView.Error:
            print(self.errors(), file=sys.stderr)
            sys.exit(-1)
        self.setTitle("Nexus Geometry Test App")
        self.setResizeMode(QQuickView.SizeRootObjectToView)
