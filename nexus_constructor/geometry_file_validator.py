from PySide2.QtCore import QObject, QUrl, Slot
from nexusutils.readwriteoff import parse_off_file
from stl import mesh
from io import TextIOWrapper
from os.path import splitext


def _validate_geometry_file(file: TextIOWrapper, filename: str):
    file_extension = splitext(filename)[-1].lower()
    if file_extension == ".off":
        try:
            if parse_off_file(file) is None:
                # An invalid file can cause the function to return None
                return False
        except (ValueError, TypeError, StopIteration, IndexError):
            # File is invalid
            return False

    elif file_extension == ".stl":
        try:
            try:
                mesh.Mesh.from_file("", fh=file, calculate_normals=False)
            except UnicodeDecodeError:
                # File is in binary format - load it again
                with open(filename, "rb") as file:
                    mesh.Mesh.from_file("", fh=file, calculate_normals=False)
        except (TypeError, AssertionError, RuntimeError, ValueError):
            # File is invalid
            return False

    else:
        # File has unrecognised/no extension
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
