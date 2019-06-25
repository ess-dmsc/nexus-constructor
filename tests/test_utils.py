from nexus_constructor.utils import validate_line_edit


class DummyLineEdit:
    def setStyleSheet(self, str):
        self.stylesheet = str

    def setToolTip(self, str):
        self.toolTip = str


def test_GIVEN_invalid_WHEN_validating_line_edit_THEN_line_edit_turns_red():
    line_edit = DummyLineEdit()
    validate_line_edit(line_edit, False)
    assert "background-color: #f6989d" in line_edit.stylesheet


def test_GIVEN_valid_WHEN_validating_line_edit_THEN_line_edit_turns_white():
    line_edit = DummyLineEdit()
    validate_line_edit(line_edit, True)
    assert "background-color: #FFFFFF" in line_edit.stylesheet


def test_GIVEN_valid_WHEN_validating_line_edit_with_tooltip_THEN_line_edit_tooltip_is_changed():
    tooltip = "this is valid"
    line_edit = DummyLineEdit()
    validate_line_edit(line_edit, True, tooltip_on_accept=tooltip)
    assert line_edit.toolTip == tooltip


def test_GIVEN_invalid_WHEN_validating_line_edit_with_tooltip_THEN_line_edit_tooltip_is_changed():
    tooltip = "this is invalid"
    line_edit = DummyLineEdit()
    validate_line_edit(line_edit, False, tooltip_on_reject=tooltip)
    assert line_edit.toolTip == tooltip


def test_GIVEN_valid_WHEN_validating_line_edit_with_no_tooltip_THEN_tooltip_is_not_changed():
    line_edit = DummyLineEdit()
    validate_line_edit(line_edit, True)
    assert line_edit.toolTip == ""


def test_GIVEN_invalid_WHEN_validating_line_edit_with_no_tooltip_THEN_tooltip_is_not_changed():
    line_edit = DummyLineEdit()
    validate_line_edit(line_edit, False)
    assert line_edit.toolTip == ""
