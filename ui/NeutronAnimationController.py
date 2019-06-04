from PySide2.QtCore import QObject, Property, Signal
from PySide2.QtGui import QMatrix4x4, QVector3D


class NeutronAnimationController(QObject):
    def __init__(self, xOffset, yOffset, parent):
        super(NeutronAnimationController, self).__init__(parent)
        self._target = None
        self._matrix = QMatrix4x4()
        self._xOffset = xOffset
        self._yOffset = yOffset
        self._distance = 0

    def setTarget(self, t):
        self._target = t

    def getTarget(self):
        return self._target

    def setDistance(self, distance):
        self._distance = distance
        self.updateMatrix()
        self.distanceChanged.emit()
        print(self._distance)

    def getDistance(self):
        return self._distance

    def updateMatrix(self):
        self._matrix.setToIdentity()
        self._matrix.translate(QVector3D(self._xOffset, self._yOffset, self._distance))
        self._matrix.scale(0.1)

        if self._target is not None:
            self._target.setMatrix(self._matrix)

    distanceChanged = Signal()
    distance = Property(float, getDistance, setDistance, notify=distanceChanged)
