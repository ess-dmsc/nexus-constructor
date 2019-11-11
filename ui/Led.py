from PySide2.QtWidgets import QPushButton, QDesktopWidget
from PySide2.QtCore import QSize
import numpy as np

class Led(QPushButton):
    green = np.array([0xad, 0xff, 0x2f], dtype=np.uint8)
    red = np.array([0xf4, 0x37, 0x53], dtype=np.uint8)
    yellow = np.array([0xff, 0xff, 0x00], dtype=np.uint8)
    white = np.array([0xff, 0xff, 0xff], dtype=np.uint8)

    def __init__(self, parent):
        super().__init__()

        self._qss = 'QPushButton {{ \
                                   border: 3px solid lightgray; \
                                   border-radius: {}px; \
                                   background-color: \
                                       QLinearGradient( \
                                           y1: 0, y2: 1, \
                                           stop: 0 white, \
                                           stop: 0.2 #{}, \
                                           stop: 0.8 #{}, \
                                           stop: 1 #{} \
                                       ); \
                                 }}'
        self._on_qss = ''
        self._off_qss = ''

        self._status = False
        self._end_radius = 0

        # Properties that will trigger changes on qss.
        self.__on_color = None
        self.__off_color = None
        self.__shape = None
        self.__height = 0

        self._on_color = Led.green
        self._off_color = Led.red
        self._height = self.sizeHint().height()

        self.set_status(False)

    def sizeHint(self):
        screenSize = QDesktopWidget().screenGeometry(-1)
        base_w = 20
        base_h = 20
        width = int(base_w * screenSize.height()/1080)
        height = int(base_h * screenSize.height()/1080)
        return QSize(width, height)

    def resizeEvent(self, event):
        self._height = self.size().height()
        QPushButton.resizeEvent(self, event)

    def setFixedSize(self, width, height):
        self._height = height
        QPushButton.setFixedSize(self, height, height)

    # ============================================================== Properties
    @property
    def _on_color(self):
        return self.__on_color

    @_on_color.setter
    def _on_color(self, color):
        self.__on_color = color
        self._update_on_qss()

    @_on_color.deleter
    def _on_color(self):
        del self.__on_color

    @property
    def _off_color(self):
        return self.__off_color

    @_off_color.setter
    def _off_color(self, color):
        self.__off_color = color
        self._update_off_qss()

    @_off_color.deleter
    def _off_color(self):
        del self.__off_color

    @property
    def _shape(self):
        return self.__shape

    @_shape.setter
    def _shape(self, shape):
        self.__shape = shape
        self._update_end_radius()
        self._update_on_qss()
        self._update_off_qss()
        self.set_status(self._status)

    @_shape.deleter
    def _shape(self):
        del self.__shape

    @property
    def _height(self):
        return self.__height

    @_height.setter
    def _height(self, height):
        self.__height = height
        self._update_end_radius()
        self._update_on_qss()
        self._update_off_qss()
        self.set_status(self._status)

    @_height.deleter
    def _height(self):
        del self.__height

    # ================================================================= Methods
    def _update_on_qss(self):
        color, grad = self._get_gradient(self.__on_color)
        self._on_qss = self._qss.format(self._end_radius, grad, color, color)

    def _update_off_qss(self):
        color, grad = self._get_gradient(self.__off_color)
        self._off_qss = self._qss.format(self._end_radius, grad, color, color)

    def _get_gradient(self, color):
        grad = ((self.white - color) / 2).astype(np.uint8) + color
        grad = '{:02X}{:02X}{:02X}'.format(grad[0], grad[1], grad[2])
        color = '{:02X}{:02X}{:02X}'.format(color[0], color[1], color[2])
        return color, grad

    def _update_end_radius(self):
        self._end_radius = int(self.__height / 2)

    def _toggle_on(self):
        self.setStyleSheet(self._on_qss)

    def _toggle_off(self):
        self.setStyleSheet(self._off_qss)

    def set_shape(self, shape):
        self._shape = shape

    def set_status(self, status):
        self._status = True if status else False
        if self._status is True:
            self._toggle_on()
        else:
            self._toggle_off()

    def turn_on(self, status=True):
        self.set_status(status)

    def turn_off(self, status=False):
        self.set_status(status)

    def is_on(self):
        return True if self._status is True else False

    def is_off(self):
        return True if self._status is False else False