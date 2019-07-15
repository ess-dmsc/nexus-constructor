from PySide2.QtCore import Signal, QObject
from PySide2.QtGui import QValidator
import pint
import os
from typing import List
import numpy as np
from enum import Enum

from PySide2.QtWidgets import QComboBox


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

    def validate(self, input: str, pos: int):
        if not input:
            self.is_valid.emit(False)
            return QValidator.Intermediate
        if not self.is_file(input):
            self.is_valid.emit(False)
            return QValidator.Intermediate
        for suffixes in self.file_types.values():
            for suff in suffixes:
                if input.endswith(f".{suff}"):
                    self.is_valid.emit(True)
                    return QValidator.Acceptable
        self.is_valid.emit(False)
        return QValidator.Invalid

    def is_file(self, input):
        return os.path.isfile(input)

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
    "String": np.string_,
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
                DATASET_TYPE[self.dataset_type_combo.currentText()](input)
            except ValueError:
                return self._emit_and_return(False)
        return self._emit_and_return(True)

    def _emit_and_return(self, valid: bool) -> QValidator.State:
        self.is_valid.emit(valid)
        return QValidator.Acceptable if valid else QValidator.Intermediate

    is_valid = Signal(bool)
