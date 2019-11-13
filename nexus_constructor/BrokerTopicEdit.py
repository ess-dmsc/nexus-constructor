from PySide2 import QtCore, QtGui, QtWidgets
import re


def validate_line_edit(
    line_edit: QtWidgets,
    QWidget,
    is_valid: bool,
    tooltip_on_reject="",
    tooltip_on_accept="",
    suggestion_callable=None,
):
    """
    Sets the line edit colour to red if field is invalid or white if valid. Also sets the tooltips if provided.
    :param line_edit: The line edit object to apply the validation to.
    :param is_valid: Whether the line edit field contains valid text
    :param suggestion_callable: A callable that returns the suggested alternative if not valid.
    :param tooltip_on_accept: Tooltip to display if line edit is valid.
    :param tooltip_on_reject: Tooltip to display if line edit is invalid.
    :return: None.
    """
    colour = "white" if is_valid else "red"
    palette = line_edit.palette()
    palette.setColor(line_edit.backgroundRole(), QtGui.QColor(colour))
    line_edit.setPalette(palette)
    line_edit.setAutoFillBackground(True)
    if "Suggestion" in tooltip_on_reject and callable(suggestion_callable):
        tooltip_on_reject += suggestion_callable()
    line_edit.setToolTip(tooltip_on_accept) if is_valid else line_edit.setToolTip(
        tooltip_on_reject
    )


def extract_addr_and_topic(in_string):
    correct_string_re = re.compile(

    )  # noqa: W605
    match_res = re.match(correct_string_re, in_string)
    if match_res is not None:
        return match_res.group(2), match_res.group(7)
    return None


class BrokerTopicEdit(QtWidgets.QLineEdit):
    addr_topic_re = re.compile("""(\s*((([^/?#:]+)+)(:(\d+))?)/([a-zA-Z0-9._-]+)\s*)""")
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.textChanged.connect(self.onTextChanged)
        self._valid = False

    def onTextChanged(self, new_text):
        print("New text: {}".format(new_text))
