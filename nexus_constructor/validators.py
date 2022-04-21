import os
import re
from enum import Enum
from typing import Callable, List, Optional

import numpy as np
import pint
from nexusutils.readwriteoff import parse_off_file
from PySide2.QtCore import QObject, Signal
from PySide2.QtGui import QIntValidator, QValidator
from PySide2.QtWidgets import QComboBox, QRadioButton, QWidget, QListWidget
from stl import mesh

from nexus_constructor.common_attrs import SCALAR
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP
from nexus_constructor.unit_utils import (
    units_are_expected_dimensionality,
    units_are_recognised_by_pint,
    units_have_magnitude_of_one,
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


def units_are_recognised(unit_string: str) -> bool:
    try:
        return units_are_recognised_by_pint(unit_string)
    except pint.errors.DefinitionSyntaxError:
        return False


class UnitValidator(QValidator):
    """
    Validator to ensure the the text entered is a valid unit of length.
    """

    ureg = pint.UnitRegistry()

    def __init__(self, expected_dimensionality=None):
        super().__init__()
        self.expected_dimensionality = expected_dimensionality

    def validate(self, input: str, pos: int):

        if not (
            units_are_recognised(input)
            and (
                True
                if self.expected_dimensionality is None
                else units_are_expected_dimensionality(
                    input, self.expected_dimensionality
                )
            )
            and units_have_magnitude_of_one(input)
        ):
            self.is_valid.emit(False)
            return QValidator.Intermediate

        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)


class AttributeNameValidator(QValidator):
    """
    Validator to ensure that attributes are valid with respect to name.
    """

    def __init__(self, get_attr_names: Callable, invalid_names: List = None):
        super().__init__()
        self.invalid_names = ["units"]
        if invalid_names:
            self.invalid_names += invalid_names
        self.get_attr_names = get_attr_names

    def validate(self, input: str, pos: int):
        attr_names = self.get_attr_names()
        if not input or input in self.invalid_names:
            self.is_valid.emit(False)
            return QValidator.Intermediate
        if attr_names.count(input) > 1:
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
        self.nx_class_is_valid = True
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

    def set_nx_class_valid(self, is_valid):
        self.nx_class_is_valid = is_valid
        self.validate_ok()

    def validate_ok(self):
        """
        Validates the fields in order to dictate whether the OK button should be disabled or enabled.
        :return: None, but emits the isValid signal.
        """
        unacceptable = [
            not self.nx_class_is_valid,
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


class FieldValueValidator(QValidator):
    """
    Validates the field value line edit to check that the entered string is castable to the selected numpy type.
    """

    def __init__(
        self,
        field_type_combo: QComboBox,
        dataset_type_combo: QComboBox,
        scalar_text: str = SCALAR,
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
        if self.field_type_combo.currentText() == self.scalar:
            try:
                VALUE_TYPE_TO_NP[self.dataset_type_combo.currentText()](input)
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
        else:
            try:
                self.dtype(input)
            except ValueError:
                self.is_valid.emit(False)
                return QValidator.Intermediate

        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)


class CommandDialogFileNameValidator(QValidator):
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


class CommandDialogOKValidator(QObject):
    def __init__(self):
        super().__init__()
        self.filename_valid = False
        self.broker_valid = False

    def set_filename_valid(self, is_valid: bool):
        self.filename_valid = is_valid
        self.validate_ok()

    def set_broker_valid(self, is_valid: bool):
        self.broker_valid = is_valid
        self.validate_ok()

    def validate_ok(self):
        self.is_valid.emit(not any([not self.broker_valid, not self.filename_valid]))

    is_valid = Signal(bool)


class BrokerAndTopicValidator(QValidator):
    def __init__(self):
        super().__init__()

    @staticmethod
    def extract_addr_and_topic(in_string):
        correct_string_re = re.compile(
            "(\s*((([^/?#:]+)+)(:(\d+))?)/([a-zA-Z0-9._-]+)\s*)"  # noqa: W605
        )
        match_res = re.match(correct_string_re, in_string)
        if match_res is not None:
            return match_res.group(2), match_res.group(7)
        return None

    def validate(self, input: str, pos: int) -> QValidator.State:
        if self.extract_addr_and_topic(input) is not None:
            self.is_valid.emit(True)
            return QValidator.Acceptable
        self.is_valid.emit(False)
        return QValidator.Intermediate

    is_valid = Signal(bool)


class NoEmptyStringValidator(QValidator):
    """
    Ensure that the provided string is not empty.
    """
    def __init__(self):
        super().__init__()

    def validate(self, input: str, pos: int) -> QValidator.State:
        if input == "":
            self.is_valid.emit(False)
            return QValidator.Intermediate
        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)


from nexus_constructor.model.group import Group


class SchemaSelectionValidator(QValidator):
    """
    Multiple schemas of the same type or some combinations of schemas in the same group are not allowed. Check/verify this.
    """

    def __init__(self, ):
        super().__init__()
        self.parent_group: Optional[Group] = None

    def set_group(self, group: Optional[Group] = None):
        self.parent_group = group

    def validate(self, input: str, pos: int) -> QValidator.State:
        if not self.parent_group:
            self.is_valid.emit(True)
            return QValidator.Acceptable
        list_of_writer_modules = [m.writer_module for m in self.parent_group.children if hasattr(m, "writer_module")]
        if list_of_writer_modules.count(input) > 1:
            self.is_valid.emit(False)
            return QValidator.Intermediate
        self.is_valid.emit(True)
        return QValidator.Acceptable

    is_valid = Signal(bool)
