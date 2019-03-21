from PySide2.QtCore import QObject, QUrl, Slot
from nexusutils.readwriteoff import parse_off_file
from stl import mesh


class GeometryFileValidator(QObject):
    @Slot(QUrl, result=bool)
    def validate_geometry_file(self, file_url: QUrl):

        filename = file_url.toString(
            options=QUrl.FormattingOptions(QUrl.PreferLocalFile)
        )
        ext = filename.lower()[-3:]

        if ext == "off":
            try:
                with open(filename) as file:
                    if parse_off_file(file) is None:
                        # In some cases a bad file causes the function to return None
                        return False
            except (ValueError, TypeError, StopIteration):
                # File is invalid
                return False

        elif ext == "stl":
            try:
                mesh.Mesh.from_file(filename, calculate_normals=False)
            except (TypeError, AssertionError, RuntimeError, ValueError):
                # File is invalid
                return False

        return True
