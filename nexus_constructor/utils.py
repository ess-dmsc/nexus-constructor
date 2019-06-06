from PySide2.QtWidgets import QFileDialog
from nexus_constructor.file_dialog_options import FILE_DIALOG_NATIVE


def file_dialog(is_save, caption, filter):
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
