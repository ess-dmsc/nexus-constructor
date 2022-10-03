import time

from PySide6 import QtGui
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtCore import Qt


class InstrumentZooming3DWindow(Qt3DExtras.Qt3DWindow):
    def __init__(self, component_root_entity, main_window):
        """
        A custom 3D window that only zooms in on the instrument components when the escape key is pressed.
        """
        super().__init__()
        self.component_root_entity = component_root_entity
        self.main_window = main_window

        render_settings = self.renderSettings()
        picking_settings = render_settings.pickingSettings()
        picking_settings.setFaceOrientationPickingMode(
            Qt3DRender.QPickingSettings.FrontAndBackFace
        )
        picking_settings.setPickMethod(
            Qt3DRender.QPickingSettings.BoundingVolumePicking
        )  # BoundingVolumePicking #TrianglePicking
        picking_settings.setPickResultMode(Qt3DRender.QPickingSettings.NearestPick)

        self.last_press_time = 0

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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_press_time = time.time()
            for e in self.component_root_entity.children():
                try:
                    if e.inside:
                        e.clicked = True
                        self.main_window.model.signals.entity_selected.emit(e)
                    elif not e.inside:
                        e.removeComponent(e.hoover_material)
                        e.addComponent(e.true_material)
                        e.clicked = False
                except Exception:
                    pass
