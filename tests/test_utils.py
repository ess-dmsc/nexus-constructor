import os

from mock import Mock

from nexus_constructor.component_type import make_dictionary_of_class_definitions
from nexus_constructor.unique_name import generate_unique_name
from nexus_constructor.ui_utils import validate_line_edit


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
    assert ("background-color: #FFFFFF" in line_edit.stylesheet)


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


def test_GIVEN_suggestion_callable_WHEN_validating_line_edit_THEN_callable_is_called():
    line_edit = DummyLineEdit()
    suggestion = Mock(side_effect="test")

    validate_line_edit(
        line_edit,
        False,
        tooltip_on_reject="Suggestion: ",
        suggestion_callable=suggestion,
    )

    assert suggestion.called_once()


def test_GIVEN_suggestion_callable_WHEN_validating_line_edit_with_valid_line_edit_THEN_callable_is_not_called_even_if_suggestion_in_name():
    line_edit = DummyLineEdit()
    suggestion = Mock(side_effect="test")

    validate_line_edit(
        line_edit,
        True,
        tooltip_on_reject="Suggestion: ",
        suggestion_callable=suggestion,
    )

    assert suggestion.not_called()


class DummyComponent:
    def __init__(self, name: str):
        self.name = name


def test_GIVEN_unique_name_WHEN_generating_unique_name_THEN_returns_unchanged_name():
    name = "something"
    assert generate_unique_name(name, []) == name


def test_GIVEN_name_already_in_list_WHEN_generating_unique_name_THEN_returns_changed_name():
    comp = DummyComponent("something")
    assert generate_unique_name(comp.name, [comp]) == comp.name + "1"


def test_GIVEN_name_with_1_in_already_WHEN_generating_unique_name_THEN_number_is_appended_to_the_suffix_of_the_name():
    comp = DummyComponent("something1")

    assert (
        generate_unique_name(
            comp.name, [DummyComponent("something1"), DummyComponent("something2")]
        )
        == comp.name + "1"
    )


def test_GIVEN_name_with_1_as_suffix_and_name_with_11_already_in_list_WHEN_generating_unique_name_THEN_following_number_is_incremented_and_name_is_unique():
    comp = DummyComponent("something1")

    assert (
        generate_unique_name(comp.name, [comp, DummyComponent(comp.name + "1")])
    ) == "something12"


NX_CLASS_DEFINITIONS = make_dictionary_of_class_definitions(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "definitions")
)[1]
