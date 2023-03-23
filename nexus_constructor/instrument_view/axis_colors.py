from enum import Enum

from PySide6.QtGui import QColor


class AxisColors(Enum):
    X = QColor(255, 0, 0)
    Y = QColor(0, 255, 0)
    Z = QColor(0, 0, 255)
