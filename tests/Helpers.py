from PySide2 import QtCore
from PySide2.QtGui import QWindow
from PySide2.QtQuick import QQuickItem
from PySide2.QtTest import QTest


# pytest-qt's qtbot.mouseClick() only works directly on QtWidget's elements, not qml's.
# Fortunately, the method it calls down to has an overload
# that takes a position and a QWindow, which QML is compatible with.
def click_object(object: QQuickItem, parentWindow: QWindow):
    point = object.mapToScene(QtCore.QPoint(0, 0)).toPoint()
    point.setX(point.x() + (object.width() / 2))
    point.setY(point.y() + (object.height() / 2))
    QTest.mouseClick(parentWindow, QtCore.Qt.LeftButton, QtCore.Qt.KeyboardModifiers(), point)


# Searches for an item with a given objectName in an items child items using a depth first search
def tree_search_items(item: QQuickItem, targetobjectname: str):
    for child in item.childItems():
        if child.objectName() == targetobjectname:
            return child
        next = tree_search_items(child, targetobjectname)
        if next is not None:
            return next
    return None