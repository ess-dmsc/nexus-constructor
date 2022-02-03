from unittest.mock import Mock

import pytest

from nexus_constructor.main_window import QDialogCustom as QDialog
from nexus_constructor.model.model import Entry, Model
from nexus_constructor.pixel_options import PixelOptions
from nexus_constructor.validators import PixelValidator
from tests.geometry.chopper_test_helpers import chopper_details  # noqa: F401


@pytest.fixture(scope="function")
def template(qtbot) -> QDialog:
    q_dialog = QDialog()
    q_dialog.disable_msg_box()
    return q_dialog


@pytest.fixture(scope="function")
def entry() -> Entry:
    return Entry()


@pytest.fixture(scope="function")
def model() -> Model:
    return Model()


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
