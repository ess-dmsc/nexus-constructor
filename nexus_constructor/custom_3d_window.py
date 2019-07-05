from PySide2 import QtGui
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtCore import Qt


class Custom3DWindow(Qt3DExtras.Qt3DWindow):
    def __init__(self):
        super().__init__()
        self.component_root_entity = None
        self.prev_position = None

    def set_component_root_entity(self, component_root_entity):
        self.component_root_entity = component_root_entity

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            print("Camera position upon pressing esc", self.camera().position())
            event.accept()

    def print_camera_position(self):
        print("Camera position after calling viewEntity", self.camera().position())

    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.camera().viewEntity(self.component_root_entity)
            self.print_camera_position()
