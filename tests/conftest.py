# import uuid
from unittest.mock import Mock

import h5py
import pytest
from PySide2.QtWidgets import QDialog

# from nexus_constructor.instrument import Instrument
# from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.model.entry import Instrument
from nexus_constructor.pixel_options import PixelOptions
from nexus_constructor.validators import PixelValidator
from tests.chopper_test_helpers import chopper_details  # noqa: F401

# from tests.test_utils import NX_CLASS_DEFINITIONS


@pytest.fixture(scope="function")
def template(qtbot) -> QDialog:
    return QDialog()


# @pytest.fixture(scope="function")
# def nexus_wrapper() -> NexusWrapper:
#     nexus_wrapper = NexusWrapper(str(uuid.uuid4()))
#     yield nexus_wrapper
#     nexus_wrapper.nexus_file.close()
#
#
@pytest.fixture(scope="function")
def instrument() -> Instrument:
    return Instrument()


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


class InMemoryFile(object):
    def __init__(self, filename):
        self.file_obj = h5py.File(
            filename, mode="x", driver="core", backing_store=False
        )

    def __enter__(self):
        return self.file_obj

    def __exit__(self, type, value, traceback):
        self.file_obj.close()


@pytest.fixture
def file():
    with InMemoryFile("test_file") as file:
        yield file
