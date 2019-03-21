from PySide2.QtCore import QObject, QUrl, Slot
from nexusutils.readwriteoff import parse_off_file
from stl import mesh
from io import TextIOWrapper


def _validate_geometry_file(file: TextIOWrapper, filename: str):
    file_extension = filename.lower()[-3:]
    if file_extension == "off":
        try:
            if parse_off_file(file) is None:
                return False
        except (ValueError, TypeError, StopIteration, IndexError):
            # File is invalid
            return False

    elif file_extension == "stl":
        try:
            mesh.Mesh.from_file("", fh=file, calculate_normals=False)
        except (TypeError, AssertionError, RuntimeError, ValueError):
            return False

    return True


class GeometryFileValidator(QObject):
    @Slot(QUrl, result=bool)
    def validate_geometry_file(self, file_url: QUrl):

        filename = file_url.toString(
            options=QUrl.FormattingOptions(QUrl.PreferLocalFile)
        )

        with open(filename) as file:
            return _validate_geometry_file(file, filename)
