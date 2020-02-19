import pytest
from PySide2.QtGui import QStandardItemModel

from nexus_constructor.file_writer_ctrl_window import FileWriterCtrl, File, FileWriter
from nexus_constructor.validators import BrokerAndTopicValidator


def test_UI_GIVEN_nothing_WHEN_creating_filewriter_control_window_THEN_broker_field_defaults_are_set_correctly(
    qtbot, instrument
):
    window = FileWriterCtrl(instrument)

    qtbot.addWidget(window)

    assert not window.command_broker_edit.text()
    assert window.command_broker_led.is_off()
    assert not window.command_broker_change_timer.isActive()

    assert not window.status_broker_edit.text()
    assert window.status_broker_led.is_off()
    assert not window.status_broker_change_timer.isActive()


def test_UI_GIVEN_nothing_WHEN_creating_filewriter_control_window_THEN_broker_validators_are_set_correctly(
    qtbot, instrument
):
    window = FileWriterCtrl(instrument)

    qtbot.addWidget(window)

    assert isinstance(window.status_broker_edit.validator(), BrokerAndTopicValidator)
    assert isinstance(window.command_broker_edit.validator(), BrokerAndTopicValidator)
    assert (
        window.command_broker_edit.validator() != window.status_broker_edit.validator()
    )  # make sure they are different objects so that both edits are validated independently from each other.


@pytest.mark.parametrize(
    "test_input", [FileWriter("test", 0), File("test", 0, "123", "321")]
)
def test_UI_GIVEN_time_string_WHEN_setting_time_THEN_last_time_is_stored(test_input):
    model = QStandardItemModel()
    current_time = "12345678"
    new_time = "23456789"
    FileWriterCtrl._set_time(model, test_input, current_time, new_time)
    assert test_input.last_time == current_time


def test_UI_GIVEN_no_files_WHEN_stop_file_writing_is_clicked_THEN_button_is_disabled(
    qtbot, instrument
):
    window = FileWriterCtrl(instrument)
    qtbot.addWidget(window)
    window.files_list.selectedIndexes = lambda: []

    window.file_list_clicked()

    assert not window.stop_file_writing_button.isEnabled()


def UI_GIVEN_files_WHEN_stop_file_writing_is_clicked_THEN_button_is_enabled(
    qtbot, instrument
):
    window = FileWriterCtrl(instrument)
    qtbot.addWidget(window)
    window.files_list.selectedIndexes = lambda: [
        1,
        2,
        3,
    ]  # Can be any list so doesn't matter what's in here

    window.file_list_clicked()

    assert window.stop_file_writing_button.isEnabled()
