import sys

from PySide2.QtCore import QPoint, Qt
from PySide2.QtWidgets import QAbstractButton, QDialog
from pytestqt.qtbot import QtBot

RUNNING_ON_WINDOWS = sys.platform.startswith("win")


def systematic_button_press(qtbot: QtBot, template: QDialog, button: QAbstractButton):
    """
    Left clicks on a button after finding the position to click using a systematic search.
    :param qtbot: The qtbot testing tool.
    :param template: The window/widget that holds an AddComponentDialog.
    :param button: The button to press.
    """
    point = find_button_press_position(button)

    if point is not None:
        qtbot.mouseClick(button, Qt.LeftButton, pos=point)
    else:
        qtbot.mouseClick(button, Qt.LeftButton)

    show_and_close_window(qtbot, template)


def find_button_press_position(button: QAbstractButton):
    """
    Systematic way of making sure a button press works. Goes through every point in the widget until it finds one that
    returns True for the `hitButton` method.
    :param button: The radio button to click.
    :return: A QPoint indicating where the button must be clicked in order for its event to be triggered.
    """
    width = button.geometry().width()
    height = button.geometry().height()

    for x in range(1, width):
        for y in range(1, height):
            click_point = QPoint(x, y)
            if button.hitButton(click_point):
                return click_point
    return None


def show_and_close_window(qtbot: QtBot, template: QDialog):
    """
    Function for displaying and then closing a window/widget. This appears to be necessary in order to make sure
    some interactions with the UI are recognised. Otherwise the UI can behave as though no clicks/button presses/etc
    actually took place which then causes tests to fail even though they ought to pass in theory.
    :param qtbot: The qtbot testing tool.
    :param template: The window/widget to be opened.
    """
    template.show()
    qtbot.waitForWindowShown(template)


def show_window_and_wait_for_interaction(qtbot: QtBot, template: QDialog):
    """
    Helper method that allows you to examine a window during testing. Just here for convenience.
    Does nothing if the test is running on Windows because this is bad for Jenkins.
    :param qtbot: The qtbot testing tool.
    :param template: The window/widget to be opened.
    """
    if RUNNING_ON_WINDOWS:
        return
    template.show()
    qtbot.stopForInteraction()
