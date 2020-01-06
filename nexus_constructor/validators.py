import h5py
from PySide2.QtCore import Signal, QObject
from PySide2.QtGui import QValidator, QIntValidator
import pint
import os
from typing import List
import numpy as np
from enum import Enum

from PySide2.QtWidgets import QComboBox, QWidget, QRadioButton
from nexusutils.readwriteoff import parse_off_file
from stl import mesh

from nexus_constructor.unit_utils import (
    units_are_recognised_by_pint,
    units_are_expected_type,
    units_have_magnitude_of_one,
    METRES,
)

HDF_FILE_EXTENSIONS = ("nxs", "hdf", "hdf5")


class NullableIntValidator(QIntValidator):
    """
    A validator that accepts integers as well as empty input.
    """

    def __init__(self, bottom=None):

        super().__init__()

        if bottom is not None:
            super().setBottom(bottom)

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

        if not (
            units_are_recognised_by_pint(input)
            and units_are_expected_type(input, METRES)
            and units_have_magnitude_of_one(input)
        ):
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

    def __init__(self, list_model: List, invalid_names=None):
        super().__init__()
        if invalid_names is None:
            invalid_names = []
        self.list_model = list_model
        self.invalid_names = invalid_names

    def validate(self, input: str, pos: int):
        if not input or input in self.invalid_names:
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


class PixelValidator(QObject):
    def __init__(
        self,
        pixel_options: QWidget,
        pixel_grid_button: QRadioButton,
        pixel_mapping_button: QRadioButton,
    ):
        """
        Validates the pixel-related input and informs the OKValidator for the Add Component Window of any changes.
        :param pixel_options: The PixelOptions object that holds pixel-related UI elements.
        :param pixel_grid_button: The pixel grid radio button.
        :param pixel_mapping_button: The pixel mapping radio button.
        """
        super().__init__()
        self.pixel_options = pixel_options
        self.pixel_grid_button = pixel_grid_button
        self.pixel_grid_is_valid = True
        self.pixel_mapping_button = pixel_mapping_button
        self.pixel_mapping_is_valid = False

    def set_pixel_mapping_valid(self, is_valid: bool):
        """
        Set the validity of the pixel mapping and inform the OKValidator of the change.
        :param is_valid: Whether or not the pixel mapping is valid.
        """
        self.pixel_mapping_is_valid = is_valid
        self.inform_ok_validator()

    def set_pixel_grid_valid(self, is_valid: bool):
        """
        Set the validity of the pixel grid and inform the OKValidator of the change.
        :param is_valid: Whether or not the pixel grid is valid.
        """
        self.pixel_grid_is_valid = is_valid
        self.inform_ok_validator()

    def unacceptable_pixel_states(self):
        """
        Determines if the current input in the pixel options is valid.
        """

        # Return nothing if the PixelOptions widget isn't presently visible. This will cause the OKValidator to not take
        # the contents of the pixel-related fields into account when assessing the overall validity of the Add Component
        # input.
        if not self.pixel_options.isVisible():
            return []

        # If the PixelOptions widget is visible then return the state of the radio buttons and their related inputs.
        return [
            self.pixel_grid_button.isChecked() and not self.pixel_grid_is_valid,
            self.pixel_mapping_button.isChecked() and not self.pixel_mapping_is_valid,
        ]

    def inform_ok_validator(self):
        """
        Sends a signal to the OKValidator that tells it to perform another validity check.
        :return:
        """
        self.reassess_validity.emit()

    reassess_validity = Signal()


class OkValidator(QObject):
    """
    Validator to enable the OK button. Several criteria have to be met before this can occur depending on the geometry type.
    """

    def __init__(
        self,
        no_geometry_button: QRadioButton,
        mesh_button: QRadioButton,
        pixel_validator: PixelValidator,
    ):
        super().__init__()
        self.name_is_valid = False
        self.file_is_valid = False
        self.units_are_valid = False
        self.no_geometry_button = no_geometry_button
        self.mesh_button = mesh_button
        self.pixel_validator = pixel_validator
        self.pixel_validator.reassess_validity.connect(self.validate_ok)

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
        ] + self.pixel_validator.unacceptable_pixel_states()
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

    def __init__(
        self,
        field_type_combo: QComboBox,
        dataset_type_combo: QComboBox,
        scalar_text: str = "Scalar",
    ):
        super().__init__()
        self.field_type_combo = field_type_combo
        self.dataset_type_combo = dataset_type_combo
        self.scalar = scalar_text

    def validate(self, input: str, pos: int) -> QValidator.State:
        """
        Validates against being blank and the correct numpy type
        :param input: the current string of the field value
        :param pos: mouse position cursor(ignored, just here to satisfy overriding function)
        :return: QValidator state (Acceptable, Intermediate, Invalid) - returning intermediate because invalid stops the user from typing.
        """
        if not input:  # More criteria here
            return self._emit_and_return(False)
        elif self.field_type_combo.currentText() == self.scalar:
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


class HDFLocationExistsValidator(QValidator):
    """
    For checking that a location exists in a given HDF file
    """

    def __init__(self, file: h5py.File, field_type):
        super(HDFLocationExistsValidator, self).__init__()
        self.file = file
        self.field_combo = field_type

    def validate(self, input: str, pos: int) -> QValidator.State:
        if not input:
            self._emit_and_return(False)
        if not self.field_combo.currentText == FieldType.link.value:
            self._emit_and_return(True)

        in_file = input in self.file
        return self._emit_and_return(in_file)

    def _emit_and_return(self, valid: bool) -> QValidator.State:
        self.is_valid.emit(valid)
        return QValidator.Acceptable if valid else QValidator.Intermediate

    is_valid = Signal(bool)


class CommandDialogOKButtonValidator(QValidator):
    """
    Validator to ensure item names are unique within a model that has a 'name' property

    The validationFailed signal is emitted if an entered name is not unique.
    """

    def __init__(self):
        super().__init__()

    def validate(self, input: str, pos: int) -> QValidator.State:
        if not input or not input.endswith(HDF_FILE_EXTENSIONS):
            self.is_valid.emit(False)
            return QValidator.Intermediate

        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)
