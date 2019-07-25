import os
from enum import Enum
from typing import List

import h5py
import numpy as np
import pint
from PySide2.QtCore import Signal, QObject
from PySide2.QtGui import QValidator, QIntValidator, QDoubleValidator
from PySide2.QtWidgets import QComboBox, QLineEdit
from nexusutils.readwriteoff import parse_off_file
from stl import mesh


class PixelGridIDValidator(QValidator):
    def __init__(self, fields: List[QLineEdit]):

        self.fields = fields
        super().__init__()

    def get_content_of_other_fields(self):
        return [field.text() for field in self.fields]

    def validate(self, input: str, pos: int) -> QValidator.State:

        content = self.get_content_of_other_fields()
        all_other_fields_empty = all(
            [input_from_other_field == "" for input_from_other_field in content]
        )
        all_other_fields_nonempty = all(
            [input_from_other_field != "" for input_from_other_field in content]
        )

        if input == "":
            if all_other_fields_empty:
                self.is_valid.emit(True)
                return QValidator.Acceptable
            else:
                self.is_valid.emit(False)
                return QValidator.Intermediate

        try:
            val = int(input)

            if val < 0:
                self.is_valid.emit(False)
                return QValidator.Invalid
            else:
                if all_other_fields_empty:
                    self.is_valid.emit(False)
                    return QValidator.Intermediate
                elif all_other_fields_nonempty:
                    self.is_valid.emit(True)
                    return QValidator.Acceptable
                else:
                    self.is_valid.emit(False)
                    return QValidator.Intermediate

        except ValueError:
            self.is_valid.emit(False)
            return QValidator.Invalid

    is_valid = Signal(bool)


class PixelGridRowColumnSizeValidator(QDoubleValidator):
    def __init__(self, corresponding_field: QLineEdit):
        """
        Validator for the row height and column width fields in the pixel grid options. Requires that the input is a
        float greater than zero.
        :param corresponding_field: The matching line edit for the number of rows/columns in the pixel grid. The
        validity of the input also depends on this value.
        """
        super().__init__()
        self.corresponding_field = corresponding_field

    def value_not_needed(self):
        """
        Checks to see if the input in the rows/columns field is 0 or empty. If this is the case then a value for
        row height/column width isn't needed.
        :return: Bool indicating whether the corresponding field is empty or has the number zero.
        """
        return self.corresponding_field.text() in ["0", ""]

    def validate(self, input: str, pos: int) -> QValidator.State:

        value_not_needed = self.value_not_needed()

        # Check if the input is empty
        if input == "":
            if value_not_needed:
                # Accept empty input if the corresponding field contains zero or also empty
                self.is_valid.emit(True)
                return QValidator.Acceptable
            else:
                # The corresponding field has a non-zero value, so an empty string in this field should be regarded as
                # intermediate
                self.is_valid.emit(False)
                return QValidator.Intermediate

        # Attempt to convert the value to a float
        try:
            val = float(input)
            # Reject negative values
            if val < 0:
                self.is_valid.emit(False)
                return QValidator.Invalid
            # View zero as intermediate because the user may be trying to enter a value between 1 and zero
            elif val == 0:
                self.is_valid.emit(False)
                return QValidator.Intermediate
            else:
                if value_not_needed:
                    # Return intermediate if the input is sensible but "unneeded"
                    self.is_valid.emit(False)
                    return QValidator.Intermediate
                else:
                    # Otherwise return acceptable
                    self.is_valid.emit(True)
                    return QValidator.Acceptable
        except ValueError:
            # Input that can't be converted to floats is invalid
            self.is_valid.emit(False)
            return QValidator.Invalid

    is_valid = Signal(bool)


class PixelGridRowColumnCountValidator(QValidator):
    def __init__(self, corresponding_field: QLineEdit):
        """
        Validator for inspecting the number of rows/columns entered in the pixel grid options. Checks the corresponding
        row height/column width value in order to determine input validity.
        :param corresponding_field: The line edit for the matching row height/column width field.
        """
        super().__init__()
        self.corresponding_field = corresponding_field

    def value_needed(self):
        """
        Checks to see if the corresponding row height/column width field contains a value. If this is the case then
        setting the number of rows/columns to zero shouldn't be considered valid.
        :return: A bool indicating that the row height/column width has an actual value.
        """
        return len(self.corresponding_field.text()) > 0

    def validate(self, input: str, pos: int) -> QValidator.State:

        value_needed = self.value_needed()

        # Check if the input is empty
        if input == "":
            if value_needed:
                # Return intermediate if the value is "needed"
                self.is_valid.emit(False)
                return QValidator.Intermediate
            else:
                # Otherwise accept an empty field
                self.is_valid.emit(True)
                return QValidator.Acceptable

        # Attempt to convert the value to an int
        try:
            val = int(input)

            # Reject negative numbers
            if val < 0:
                self.is_valid.emit(False)
                return QValidator.Invalid
            elif val == 0:
                # Return intermediate if a positive value is "needed"
                if value_needed:
                    self.is_valid.emit(False)
                    return QValidator.Intermediate
                else:
                    # Accept zero if a positive value isn't needed
                    self.is_valid.emit(True)
                    return QValidator.Acceptable
            else:
                if value_needed:
                    # Return acceptable if the input in both fields are sensible
                    self.is_valid.emit(True)
                    return QValidator.Acceptable
                else:
                    # Return intermediate if the input is sensible but isn't "needed"
                    self.is_valid.emit(False)
                    return QValidator.Intermediate

        except ValueError:
            self.is_valid.emit(False)
            return QValidator.Invalid

    is_valid = Signal(bool)


class NullableIntValidator(QIntValidator):
    """
    A validator that accepts integers as well as empty input.
    """

    def __init__(self, bottom=None, top=None):

        super().__init__()

        if bottom is not None:
            super().setBottom(bottom)

        if top is not None:
            super().setTop(top)

    def validate(self, input: str, pos: int):
        if input == "":
            return QValidator.Acceptable
        else:
            return super().validate(input, pos)


class UnitValidator(QValidator):
    """
    Validator to ensure the the text entered is a valid unit of length.
    """

    def __init__(self):
        super().__init__()
        self.ureg = pint.UnitRegistry()

    def validate(self, input: str, pos: int):

        # Attempt to convert the string argument to a unit
        try:
            unit = self.ureg(input)
        except (
            pint.errors.UndefinedUnitError,
            AttributeError,
            pint.compat.tokenize.TokenError,
        ):
            self.is_valid.emit(False)
            return QValidator.Intermediate

        # Attempt to find 1 metre in terms of the unit. This will ensure that it's a length.
        try:
            self.ureg.metre.from_(unit)
        except (pint.errors.DimensionalityError, ValueError):
            self.is_valid.emit(False)
            return QValidator.Intermediate

        # Reject input in the form of "2 metres," "40 cm," etc
        if unit.magnitude != 1:
            self.is_valid.emit(False)
            return QValidator.Intermediate

        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)


class NameValidator(QValidator):
    """
    Validator to ensure item names are unique within a model that has a 'name' property

    The validationFailed signal is emitted if an entered name is not unique.
    """

    def __init__(self, list_model: List):
        super().__init__()
        self.list_model = list_model

    def validate(self, input: str, pos: int):
        if not input:
            self.is_valid.emit(False)
            return QValidator.Intermediate

        names_in_list = [item.name for item in self.list_model]
        if input in names_in_list:
            self.is_valid.emit(False)
            return QValidator.Intermediate

        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)


GEOMETRY_FILE_TYPES = {"OFF Files": ["off", "OFF"], "STL Files": ["stl", "STL"]}


class GeometryFileValidator(QValidator):
    """
    Validator to ensure file exists and is the correct file type.
    """

    def __init__(self, file_types):
        """

        :param file_types: dict of file extensions that are valid.
        """
        super().__init__()
        self.file_types = file_types

    def validate(self, input: str, pos: int) -> QValidator.State:
        if not input:
            return self._emit_and_return(False)
        if not self.is_file(input):
            return self._emit_and_return(False)
        for suffixes in self.file_types.values():
            for suff in suffixes:
                if input.endswith(f".{suff}"):
                    if suff in GEOMETRY_FILE_TYPES["OFF Files"]:
                        return self._validate_off_file(input)
                    if suff in GEOMETRY_FILE_TYPES["STL Files"]:
                        return self._validate_stl_file(input)
        return self._emit_and_return(False)

    def _validate_stl_file(self, input: str) -> QValidator.State:
        try:
            try:
                mesh.Mesh.from_file(
                    "", fh=self.open_file(input), calculate_normals=False
                )
            except UnicodeDecodeError:
                # File is in binary format - load it again
                mesh.Mesh.from_file(
                    "", fh=self.open_file(input, mode="rb"), calculate_normals=False
                )
            return self._emit_and_return(True)
        except (TypeError, AssertionError, RuntimeError, ValueError):
            # File is invalid
            return self._emit_and_return(False)

    def _emit_and_return(self, is_valid: bool) -> QValidator.State:
        self.is_valid.emit(is_valid)
        if is_valid:
            return QValidator.Acceptable
        else:
            return QValidator.Intermediate

    def _validate_off_file(self, input: str) -> QValidator.State:
        try:
            if parse_off_file(self.open_file(input)) is None:
                # An invalid file can cause the function to return None
                return self._emit_and_return(False)
        except (ValueError, TypeError, StopIteration, IndexError):
            # File is invalid
            return self._emit_and_return(False)
        return self._emit_and_return(True)

    @staticmethod
    def is_file(input: str) -> bool:
        return os.path.isfile(input)

    @staticmethod
    def open_file(filename: str, mode: str = "r"):
        return open(filename, mode)

    is_valid = Signal(bool)


class OkValidator(QObject):
    """
    Validator to enable the OK button. Several criteria have to be met before this can occur depending on the geometry type.
    """

    def __init__(self, no_geometry_button, mesh_button):
        super().__init__()
        self.name_is_valid = False
        self.file_is_valid = False
        self.units_are_valid = False
        self.no_geometry_button = no_geometry_button
        self.mesh_button = mesh_button

    def set_name_valid(self, is_valid):
        self.name_is_valid = is_valid
        self.validate_ok()

    def set_file_valid(self, is_valid):
        self.file_is_valid = is_valid
        self.validate_ok()

    def set_units_valid(self, is_valid):
        self.units_are_valid = is_valid
        self.validate_ok()

    def validate_ok(self):
        """
        Validates the fields in order to dictate whether the OK button should be disabled or enabled.
        :return: None, but emits the isValid signal.
        """
        unacceptable = [
            not self.name_is_valid,
            not self.no_geometry_button.isChecked() and not self.units_are_valid,
            self.mesh_button.isChecked() and not self.file_is_valid,
        ]
        self.is_valid.emit(not any(unacceptable))

    # Signal to indicate that the fields are valid or invalid. False: invalid.
    is_valid = Signal(bool)


class FieldType(Enum):
    scalar_dataset = "Scalar dataset"
    array_dataset = "Array dataset"
    kafka_stream = "Kafka stream"
    link = "Link"
    nx_class = "NX class/group"


DATASET_TYPE = {
    "Byte": np.byte,
    "UByte": np.ubyte,
    "Short": np.short,
    "UShort": np.ushort,
    "Integer": np.intc,
    "UInteger": np.uintc,
    "Long": np.int_,
    "ULong": np.uint,
    "Float": np.single,
    "Double": np.double,
    "String": h5py.special_dtype(vlen=str),
}


class FieldValueValidator(QValidator):
    """
    Validates the field value line edit to check that the entered string is castable to the selected numpy type.
    """

    def __init__(self, field_type_combo: QComboBox, dataset_type_combo: QComboBox):
        super().__init__()
        self.field_type_combo = field_type_combo
        self.dataset_type_combo = dataset_type_combo

    def validate(self, input: str, pos: int) -> QValidator.State:
        """
        Validates against being blank and the correct numpy type
        :param input: the current string of the field value
        :param pos: mouse position cursor(ignored, just here to satisfy overriding function)
        :return: QValidator state (Acceptable, Intermediate, Invalid) - returning intermediate because invalid stops the user from typing.
        """
        if not input:  # More criteria here
            return self._emit_and_return(False)
        elif self.field_type_combo.currentText() == FieldType.scalar_dataset.value:
            try:
                if (
                    h5py.check_dtype(
                        vlen=DATASET_TYPE[self.dataset_type_combo.currentText()]
                    )
                    == str
                ):
                    return self._emit_and_return(True)
            except AttributeError:
                pass

            try:
                DATASET_TYPE[self.dataset_type_combo.currentText()](input)
            except ValueError:
                return self._emit_and_return(False)
        return self._emit_and_return(True)

    def _emit_and_return(self, valid: bool) -> QValidator.State:
        self.is_valid.emit(valid)
        return QValidator.Acceptable if valid else QValidator.Intermediate

    is_valid = Signal(bool)


class NumpyDTypeValidator(QValidator):
    """
    Check given string can be cast to the specified numpy dtype
    """

    def __init__(self, dtype: np.dtype):
        super().__init__()
        self.dtype = dtype

    def validate(self, input: str, pos: int) -> QValidator.State:
        if not input:
            self.is_valid.emit(False)
            return QValidator.Intermediate
        try:
            if h5py.check_dtype(vlen=self.dtype) == str:
                self.is_valid.emit(True)
                return QValidator.Acceptable
        except AttributeError:
            try:
                self.dtype(input)
            except ValueError:
                self.is_valid.emit(False)
                return QValidator.Intermediate

        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)
