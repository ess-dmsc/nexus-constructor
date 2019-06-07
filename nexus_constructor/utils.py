from PySide2.QtWidgets import QFileDialog
from nexus_constructor.file_dialog_options import FILE_DIALOG_NATIVE


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
        directory="",
        filter=f"{filter};;All Files (*)",
        options=options,
    )
    return filename


def validate_line_edit(
    line_edit, is_valid: bool, tooltip_on_reject="", tooltip_on_accept=""
):
    """
    Sets the line edit colour to red if field is invalid or white if valid. Also sets the tooltips if provided.
    :param tooltip_on_accept: Tooltip to display if line edit is valid.
    :param tooltip_on_reject: Tooltip to display if line edit is invalid.
    :param line_edit: The line edit object to apply the validation to.
    :param is_valid: Whether the line edit field contains valid text
    :return: None.
    """
    colour = "#FFFFFF" if is_valid else "#f6989d"
    line_edit.setStyleSheet(f"QLineEdit {{ background-color: {colour} }}")
    line_edit.setToolTip(tooltip_on_accept) if is_valid else line_edit.setToolTip(
        tooltip_on_reject
    )
