from nexus_constructor.filewriter_command_dialog import FilewriterCommandDialog


def test_UI_GIVEN_user_presses_disable_start_time_THEN_start_time_line_edit_is_disabled(
    qtbot
):
    dialog = FilewriterCommandDialog()
    assert dialog.start_time_picker.isEnabled()
    dialog.start_time_enabled.setChecked(False)
    assert not dialog.start_time_picker.isEnabled()


def test_UI_GIVEN_user_presses_disable_stop_time_THEN_stop_time_picker_is_disabled():
    dialog = FilewriterCommandDialog()
    assert dialog.stop_time_picker.isEnabled()
    dialog.stop_time_enabled.setChecked(False)
    assert dialog.stop_time_picker.isEnabled()


def test_UI_GIVEN_user_presses_enable_start_time_THEN_start_time_picker_is_enabled():
    dialog = FilewriterCommandDialog()
    assert dialog.start_time_picker.isEnabled()
    dialog.start_time_enabled.setChecked(True)
    assert dialog.start_time_picker.isEnabled()


def test_UI_GIVEN_user_presses_enable_stop_time_THEN_stop_time_picker_is_enabled():
    dialog = FilewriterCommandDialog()
    assert dialog.stop_time_picker.isEnabled()
    dialog.stop_time_enabled.setChecked(True)
    assert dialog.stop_time_picker.isEnabled()
