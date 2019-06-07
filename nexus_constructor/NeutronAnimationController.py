from PySide2.QtCore import QObject, Property, Signal
from PySide2.QtGui import QMatrix4x4, QVector3D


class NeutronAnimationController(QObject):
    def __init__(self, x_offset, y_offset, parent):
        super(NeutronAnimationController, self).__init__(parent)
        self._target = None
        self._matrix = QMatrix4x4()
        self._x_offset = x_offset
        self._y_offset = y_offset
        self._distance = 0

    def set_target(self, t):
        self._target = t

    def get_target(self):
        return self._target

    def set_distance(self, distance):
        self._distance = distance
        self.update_matrix()
        self.distanceChanged.emit()

    def get_distance(self):
        return self._distance

    def update_matrix(self):
        self._matrix.setToIdentity()
        self._matrix.translate(
            QVector3D(self._x_offset, self._y_offset, self._distance)
        )
        self._matrix.scale(0.1)

        if self._target is not None:
            self._target.setMatrix(self._matrix)

    distanceChanged = Signal()
    distance = Property(float, get_distance, set_distance, notify=distanceChanged)
