from PySide6.QtCore import Property, QObject, Signal
from PySide6.QtGui import QMatrix4x4, QVector3D


class NeutronAnimationController(QObject):
    """
    A tool for creating an animation by instructing the neutron entities to move through the cylinder.
    :param x_offset: The x-coordinate of the neutron's position as it moves through the beam.
    :param y_offset: The y-coordinate of the neutron's position as it moves through the beam.
    :param parent: The neutron's QTransform object.
    """

    def __init__(self, x_offset, y_offset, parent):
        super(NeutronAnimationController, self).__init__(parent)
        self._target = None
        self._matrix = QMatrix4x4()
        self._x_offset = x_offset
        self._y_offset = y_offset
        self._distance = 0

    def set_target(self, t):
        """
        Sets the target QTransform for the animation.
        :param t: A QTransform that is associated with a neutron entity.
        """
        self._target = t

    def get_target(self):
        """
        :return: The QTransform that this NeutronAnimationController manages.
        """
        return self._target

    def set_distance(self, distance):
        """
        Updates the current distance of the neutron while its animation is running. Updates the transformation matrix
        and emits the `distance_changed` signal.
        :param distance: The new distance of the neutron for the next step of the animation.
        """
        self._distance = distance
        self.update_matrix()
        self.distance_changed.emit()

    def get_distance(self):
        """
        :return: The current distance of the neutron.
        """
        return self._distance

    def update_matrix(self):
        """
        Use the updated distance to construct a new transformation matrix and then apply this matrix to `self._target`.
        `set_target` needs to be called before starting the animation otherwise nothing will move.
        """
        self._matrix.setToIdentity()
        self._matrix.translate(
            QVector3D(self._x_offset, self._y_offset, self._distance)
        )
        self._matrix.scale(0.1)

        if self._target is not None:
            self._target.setMatrix(self._matrix)

    distance_changed = Signal()
    distance = Property(float, get_distance, set_distance, notify=distance_changed)
