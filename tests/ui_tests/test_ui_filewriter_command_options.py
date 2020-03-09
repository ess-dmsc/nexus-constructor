import uuid

import pytest
from PySide2.QtCore import QSettings
from nexus_constructor.filewriter_command_widget import FilewriterCommandWidget
from nexus_constructor.file_writer_ctrl_window import (
    FileWriterCtrl,
    FileWriterSettings,
    extract_bool_from_qsettings,
)
from nexus_constructor.instrument import Instrument
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper


def test_UI_GIVEN_user_presses_disable_start_time_THEN_start_time_line_edit_is_disabled(
    qtbot,
):
    dialog = FilewriterCommandWidget()
    assert dialog.start_time_picker.isEnabled()
    dialog.start_time_enabled.setChecked(False)
    assert not dialog.start_time_picker.isEnabled()


def test_UI_GIVEN_user_presses_disable_stop_time_THEN_stop_time_picker_is_disabled():
    dialog = FilewriterCommandWidget()
    assert not dialog.stop_time_picker.isEnabled()
    dialog.stop_time_enabled.setChecked(False)
    assert not dialog.stop_time_picker.isEnabled()


def test_UI_GIVEN_user_presses_enable_start_time_THEN_start_time_picker_is_enabled():
    dialog = FilewriterCommandWidget()
    assert dialog.start_time_picker.isEnabled()
    dialog.start_time_enabled.setChecked(True)
    assert dialog.start_time_picker.isEnabled()


def test_UI_GIVEN_user_presses_enable_stop_time_THEN_stop_time_picker_is_enabled():
    dialog = FilewriterCommandWidget()
    assert not dialog.stop_time_picker.isEnabled()
    dialog.stop_time_enabled.setChecked(True)
    assert dialog.stop_time_picker.isEnabled()


@pytest.fixture()
def settings():
    settings = QSettings("testing", "NCui_tests")
    yield settings
    settings.setValue(FileWriterSettings.STATUS_BROKER_ADDR, "")
    settings.setValue(FileWriterSettings.COMMAND_BROKER_ADDR, "")
    settings.setValue(FileWriterSettings.FILE_NAME, "")
    settings.setValue(FileWriterSettings.USE_START_TIME, False)
    settings.setValue(FileWriterSettings.USE_STOP_TIME, False)
    settings.setValue(FileWriterSettings.FILE_BROKER_ADDR, "")


def test_UI_settings_are_saved_when_store_settings_is_called(qtbot, settings):
    nexus_wrapper = NexusWrapper(str(uuid.uuid4()))
    instrument = Instrument(nexus_wrapper, {})
    window = FileWriterCtrl(instrument, settings)
    qtbot.addWidget(window)

    command_broker = "broker:9092/topic1"
    window.command_broker_edit.setText(command_broker)

    status_broker = "broker2:9092/topic2"
    window.status_broker_edit.setText(status_broker)

    file_broker = "broker3:9092/topic3"
    window.command_widget.broker_line_edit.setText(file_broker)

    use_start_time = True
    window.command_widget.start_time_enabled.setChecked(use_start_time)

    use_stop_time = True
    window.command_widget.stop_time_enabled.setChecked(use_stop_time)

    filename = "test.nxs"
    window.command_widget.nexus_file_name_edit.setText(filename)

    window._store_settings()
    window.close()

    assert settings.value(FileWriterSettings.COMMAND_BROKER_ADDR) == command_broker
    assert settings.value(FileWriterSettings.STATUS_BROKER_ADDR) == status_broker
    assert settings.value(FileWriterSettings.FILE_BROKER_ADDR) == file_broker
    assert (
        extract_bool_from_qsettings(settings.value(FileWriterSettings.USE_START_TIME))
        == use_start_time
    )
    assert (
        extract_bool_from_qsettings(settings.value(FileWriterSettings.USE_STOP_TIME))
        == use_stop_time
    )
    assert settings.value(FileWriterSettings.FILE_NAME) == filename


def test_UI_stored_settings_are_shown_in_window(qtbot, settings):
    command_broker = "broker:9092/topic2"
    status_broker = "broker2:9092/topic3"
    file_broker = "broker3:9092/topic4"
    use_start_time = True
    use_stop_time = False
    filename = "test2.nxs"

    settings.setValue(FileWriterSettings.STATUS_BROKER_ADDR, status_broker)
    settings.setValue(FileWriterSettings.COMMAND_BROKER_ADDR, command_broker)
    settings.setValue(FileWriterSettings.FILE_NAME, filename)
    settings.setValue(FileWriterSettings.USE_START_TIME, use_start_time)
    settings.setValue(FileWriterSettings.USE_STOP_TIME, use_stop_time)
    settings.setValue(FileWriterSettings.FILE_BROKER_ADDR, file_broker)

    nexus_wrapper = NexusWrapper(str(uuid.uuid4()))
    instrument = Instrument(nexus_wrapper, {})
    # _restore_settings should be called on construction
    window = FileWriterCtrl(instrument, settings)
    qtbot.addWidget(window)

    assert window.status_broker_edit.text() == status_broker
    assert window.command_broker_edit.text() == command_broker
    assert use_start_time == window.command_widget.start_time_enabled.isChecked()
    assert use_stop_time == window.command_widget.stop_time_enabled.isChecked()
    assert filename == window.command_widget.nexus_file_name_edit.text()
    assert file_broker == window.command_widget.broker_line_edit.text()


def test_UI_disable_stop_button_when_no_files_are_selected(qtbot, settings):
    nexus_wrapper = NexusWrapper(str(uuid.uuid4()))
    instrument = Instrument(nexus_wrapper, {})
    window = FileWriterCtrl(instrument, settings)
    qtbot.addWidget(window)

    assert not window.files_list.selectedIndexes()
    assert not window.stop_file_writing_button.isEnabled()
