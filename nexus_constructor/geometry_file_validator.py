from PySide2.QtCore import QObject, QUrl, Slot
import sys

class GeometryFileValidator(QObject):
    @Slot(QUrl, result=bool)
    def validate_geometry_file(self, file_url: QUrl):

        ext = file_url.toString(options=QUrl.FormattingOptions(QUrl.PreferLocalFile))[
            -3:
        ].lower()
        sys.stdout.write(ext)
        if ext == "off":
            return False
        elif ext == "stl":
            return False

        return True
