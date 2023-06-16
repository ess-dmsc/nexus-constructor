from typing import Optional

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QVector3D
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QLabel,
    QMessageBox,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

FILE_DIALOG_NATIVE = QFileDialog.DontUseNativeDialog


def file_dialog(is_save, caption, filter):
    """
    Creates and shows a file dialog.
    :param is_save: Whether the fial dialog should save or open files.
    :param caption: File dialog title.
    :param filter: A dict with keys being a string of the type of files and the value being a list of file extensions.
    :return: The file path of the saved or opened file.
    """
    filter_str = []
    for filetype, suffixes in filter.items():
        suffixes_str = " ".join([f"*.{suff}" for suff in suffixes])
        filter_str.append(f"{filetype} ({suffixes_str})")
    filter = ";;".join(filter_str)

    options = QFileDialog.Options()
    options |= FILE_DIALOG_NATIVE

    func = QFileDialog.getSaveFileName if is_save else QFileDialog.getOpenFileName
    filename, _ = func(
        parent=None,
        caption=caption,
        dir="",
        filter=f"{filter};;All Files (*)",
        options=options,
    )
    return filename


def validate_combobox_edit(
    combobox_edit,
    is_valid: bool,
    tooltip_on_reject="",
    tooltip_on_accept="",
    suggestion_callable=None,
):
    """
    Sets the combobox colour to red if field is invalid or white if valid. Also sets the tooltips, if provided.
    :param combobox_edit: The combobox object to apply the validation to.
    :param is_valid: Whether the combobox edit field contains valid text
    :param suggestion_callable: A callable that returns the suggested alternative if not valid.
    :param tooltip_on_accept: Tooltip to display combobox edit is valid.
    :param tooltip_on_reject: Tooltip to display combobox edit is invalid.
    :return: None.
    """
    colour = "#333333" if is_valid else "#f6989d"
    combobox_edit.setStyleSheet(f"QComboBox {{ background-color: {colour} }}")
    if "Suggestion" in tooltip_on_reject and callable(suggestion_callable):
        tooltip_on_reject += suggestion_callable()
    combobox_edit.setToolTip(
        tooltip_on_accept
    ) if is_valid else combobox_edit.setToolTip(tooltip_on_reject)


def validate_line_edit(
    line_edit,
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
    colour = "#333333" if is_valid else "#f6989d"
    line_edit.setStyleSheet(f"QLineEdit {{ background-color: {colour} }}")
    if "Suggestion" in tooltip_on_reject and callable(suggestion_callable):
        tooltip_on_reject += suggestion_callable()
    line_edit.setToolTip(tooltip_on_accept) if is_valid else line_edit.setToolTip(
        tooltip_on_reject
    )


def validate_general_widget(
    widget: QWidget,
    is_valid: bool,
):
    """
    Sets the text of a general widget to red if it is invalid or black if valid.
    :param dropdown_list: The dropdown lost.
    :param is_valid: Whether the line edit field contains valid text
    :return: None.
    """
    colour = Qt.black if is_valid else Qt.red
    pal = widget.palette()
    pal.setColor(QPalette.Text, colour)
    widget.setPalette(pal)


def qvector3d_to_numpy_array(input_vector: QVector3D) -> np.ndarray:
    return np.array([input_vector.x(), input_vector.y(), input_vector.z()]).astype(
        float
    )


def numpy_array_to_qvector3d(input_array: np.ndarray) -> QVector3D:
    return QVector3D(input_array[0], input_array[1], input_array[2])


def show_warning_dialog(
    message: str, title: str, additional_info: Optional[str] = "", parent=None
):
    msg = QMessageBox(
        QMessageBox.Warning, title, message, buttons=QMessageBox.Ok, parent=parent
    )
    msg.setInformativeText(additional_info)
    msg.show()
    msg.exec_()


class ProgressBar(QDialog):
    def __init__(self, progress_max_value: int, text: str = "Progress of process..."):
        super().__init__()
        self._one_percent_value = int(progress_max_value / 100)
        self._percentage_complete: int = 0
        self._internal_counter = 0
        self._setup_ui(text)

    def _setup_ui(self, text: str):
        self.setWindowTitle(text)
        self.setLayout(QVBoxLayout())
        self.setMinimumWidth(300)
        self._progress_bar = QProgressBar(self)
        self._progress_bar.setTextVisible(False)
        self.layout().addWidget(self._progress_bar)
        self._text_label = QLabel()
        self.layout().addWidget(self._text_label)
        self.show()

    def update_progress_bar(self):
        if self._internal_counter >= self._one_percent_value:
            self._percentage_complete += 1
            self._progress_bar.setValue(self._percentage_complete)
            self._text_label.setText(
                f"Process is {self._percentage_complete}% complete"
            )
            QApplication.processEvents()
            self._internal_counter = 0
        else:
            self._internal_counter += 1
