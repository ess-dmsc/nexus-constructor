from PySide2.QtCore import QObject, QUrl, Slot


class GeometryFileValidator(QObject):
    @Slot(QUrl, result=bool)
    def validate_geometry_file(self, file_url: QUrl):

        ext = file_url.toString(
            options=QUrl.FormattingOptions(QUrl.PreferLocalFile)
        ).lower()[-3:]

        if ext == "off":
            pass

        elif ext == "stl":
            pass
