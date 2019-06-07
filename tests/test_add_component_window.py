from nexus_constructor.addcomponentwindow import validate_line_edit


class DummyLineEdit:
    def setStyleSheet(self, str):
        self.stylesheet = str

    def styleSheet(self):
        return self.stylesheet


def test_GIVEN_invalid_WHEN_validating_line_edit_THEN_line_edit_turns_red():

    line_edit = DummyLineEdit()
    validate_line_edit(line_edit, False)
    assert "background-color: #f6989d" in line_edit.styleSheet()


def test_GIVEN_valid_WHEN_validating_line_edit_THEN_line_edit_turns_white():
    line_edit = DummyLineEdit()
    validate_line_edit(line_edit, True)
    assert "background-color: #FFFFFF" in line_edit.styleSheet()
