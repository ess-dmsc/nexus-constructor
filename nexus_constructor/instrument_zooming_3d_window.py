from PySide2 import QtGui
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtCore import Qt


class InstrumentZooming3DWindow(Qt3DExtras.Qt3DWindow):
    def __init__(self):
        """
        A custom 3D window that only zooms in on the instrument components when the escape key is pressed.
        """
        super().__init__()
        self.component_root_entity = None

    def set_component_root_entity(self, component_root_entity):
        """
        Sets the entity which is used when the viewEntity method is called. This is the entity that only contains
        instrument components.
        :param component_root_entity: The entity for the instrument components.
        """
        self.component_root_entity = component_root_entity

    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        """
        Changes the behaviour of the Escape button by having this lead to the camera viewing all the components of a
        certain entity rather than simply calling `viewAll`. Allows the superclass method to interpret the other key
        releases.
        :param event: The key event.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.camera().viewEntity(self.component_root_entity)
            return
        super().keyReleaseEvent(event)
