import sys

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QAbstractButton, QDialog
from pytestqt.qtbot import QtBot

RUNNING_ON_WINDOWS = sys.platform.startswith("win")

RED_BACKGROUND = "{ background-color: #f6989d }"
WHITE_BACKGROUND = "{ background-color: #FFFFFF }"
LINE_EDIT = "QLineEdit "
SPIN_BOX = "QSpinBox "
RED_LINE_EDIT_STYLE_SHEET = LINE_EDIT + RED_BACKGROUND
WHITE_LINE_EDIT_STYLE_SHEET = LINE_EDIT + WHITE_BACKGROUND
RED_SPIN_BOX_STYLE_SHEET = SPIN_BOX + RED_BACKGROUND
WHITE_SPIN_BOX_STYLE_SHEET = SPIN_BOX + WHITE_BACKGROUND

VALID_CUBE_OFF_FILE = (
    "OFF\n"
    "#  cube.off\n"
    "#  A cube\n"
    "8 6 0\n"
    "-0.500000 -0.500000 0.500000\n"
    "0.500000 -0.500000 0.500000\n"
    "-0.500000 0.500000 0.500000\n"
    "0.500000 0.500000 0.500000\n"
    "-0.500000 0.500000 -0.500000\n"
    "0.500000 0.500000 -0.500000\n"
    "-0.500000 -0.500000 -0.500000\n"
    "-0.500000 0.500000 0.500000\n"
    "4 0 1 3 2\n"
    "4 2 3 5 4\n"
    "4 4 5 7 6\n"
    "4 6 7 1 0\n"
    "4 1 7 5 3\n"
    "4 6 0 2 4\n"
)

VALID_OCTA_OFF_FILE = (
    "OFF\n"
    "#\n"
    "#  octa.off\n"
    "#  An octahedron.\n"
    "#\n"
    "6  8  12\n"
    "  0.0  0.0  1.0\n"
    "  1.0  0.0  0.0\n"
    "  0.0  1.0  0.0\n"
    " -1.0  0.0  0.0\n"
    "  0.0 -1.0  0.0\n"
    "  0.0  0.0 -1.0\n"
    "3  1 0 4  178 0 0\n"
    "3  4 0 3  178 0 0\n"
    "3  3 0 2  178 0 0\n"
    "3  2 0 1  178 0 0 \n"
    "3  1 5 2  178 0 0 \n"
    "3  2 5 3  178 0 0\n"
    "3  3 5 4  178 0 0\n"
    "3  4 5 1  178 0 0\n"
)


def get_expected_number_of_faces(off_file):
    """
    Finds the expected number of faces in an OFF file. Used to check this matches the number of items in a pixel
    mapping list.
    :param off_file: The OFF file.
    :return: The number of faces in the OFF file.
    """
    for line in off_file.split("\n")[1:]:
        if line[0] != "#":
            return int(line.split()[1])


CORRECT_CUBE_FACES = get_expected_number_of_faces(VALID_CUBE_OFF_FILE)
CORRECT_OCTA_FACES = get_expected_number_of_faces(VALID_OCTA_OFF_FILE)


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
