import sys
from unittest.mock import Mock

import pytest
from PySide2.QtCore import QPoint, Qt
from PySide2.QtWidgets import QAbstractButton, QDialog
from pytestqt.qtbot import QtBot

from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.instrument import Instrument
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.pixel_options import PixelOptions
from nexus_constructor.validators import PixelValidator
from tests.test_utils import DEFINITIONS_DIR

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
    "3  1 0 4  0.7 0 0\n"
    "3  4 0 3  0.7 0 0\n"
    "3  3 0 2  0.7 0 0\n"
    "3  2 0 1  0.7 0 0 \n"
    "3  1 5 2  0.7 0 0 \n"
    "3  2 5 3  0.7 0 0\n"
    "3  3 5 4  0.7 0 0\n"
    "3  4 5 1  0.7 0 0\n"
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


@pytest.fixture(scope="function")
def template(qtbot):
    return QDialog()


@pytest.fixture(scope="function")
def nexus_wrapper():
    nexus_wrapper = NexusWrapper("test")
    yield nexus_wrapper
    nexus_wrapper.nexus_file.close()


@pytest.fixture(scope="function")
def instrument(nexus_wrapper):
    return Instrument(nexus_wrapper, DEFINITIONS_DIR)


@pytest.fixture(scope="function")
def add_component_dialog(
    qtbot, template, instrument, nexus_wrapper, mock_pixel_options
):

    component = ComponentTreeModel(instrument)
    dialog = AddComponentDialog(instrument, component, definitions_dir=DEFINITIONS_DIR)
    template.ui = dialog
    template.ui.setupUi(template, mock_pixel_options)
    qtbot.addWidget(template)

    yield dialog

    # Close the file to avoid an error
    instrument.nexus.nexus_file.close()


@pytest.fixture(scope="function")
def mock_pixel_options():
    """
    Creates a mock of the PixelOptions widget. Used for some basic testing of AddComponentDialog behaviour that requires
    interaction with the PixelOptions. Testing of the PixelOptions behaviour takes place in a dedicated file.
    """
    pixel_options = Mock(spec=PixelOptions)
    pixel_options.validator = Mock(spec=PixelValidator)
    pixel_options.validator.unacceptable_pixel_states = Mock(return_value=[])

    # When the method for creating a pixel mapping is called in PixelOptions, it causes the current mapping filename
    # stored in PixelOptions to change. This behaviour is going to be mimicked with a side effect mock.
    def change_mapping_filename(filename):
        pixel_options.get_current_mapping_filename = Mock(return_value=filename)

    pixel_options.populate_pixel_mapping_list_with_mesh = Mock(
        side_effect=change_mapping_filename
    )

    # Make the filename in PixelOptions start as None as this is what the PixelOptions has after its been initialised.
    change_mapping_filename(None)

    return pixel_options
