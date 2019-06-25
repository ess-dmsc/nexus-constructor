"""Validators to be used on QML input fields"""
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from PySide2.QtCore import Property, Qt, Signal, QObject
from PySide2.QtGui import QValidator, QIntValidator
import pint
import os


class NullableIntValidator(QIntValidator):
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


class ValidatorOnListModel(QValidator):
    """
    Base class for validators that check an indexed item against other components in an InstrumentModel

    Exposes properties that can be set in QML for the component index, and instrument model.
    In QML these can be set with 'myindex' and 'model'
    A signal 'validationFailed' is included so that error messages can be displayed in the UI to explain the failure.

    Getters and setters, while un-pythonic, are required for the Qt properties system
    https://wiki.qt.io/Qt_for_Python_UsingQtProperties
    """

    def __init__(self):
        super().__init__()
        self.list_model = InstrumentModel()
        self.model_index = 0

    def get_index(self):
        return self.model_index

    def set_index(self, val: int):
        self.model_index = val

    @Signal
    def index_changed(self):
        pass

    myindex = Property(int, get_index, set_index, notify=index_changed)

    def get_model(self):
        return self.list_model

    def set_model(self, val: InstrumentModel):
        self.list_model = val

    @Signal
    def model_changed(self):
        pass

    model = Property("QVariant", get_model, set_model, notify=model_changed)

    validation_failed = Signal()


class TransformParentValidator(ValidatorOnListModel):
    """
    Validator to prevent circular transform parent dependencies being created in an instrument model
    """

    def __init__(self):
        super().__init__()

    def validate(self, proposed_parent_name: str, pos: int):
        """
        Validates the input as the name of a component's transform parent to check it won't cause a circular dependency

        The signal 'validationFailed' is emitted only if a circular dependency is found
        (http://doc.qt.io/qt-5/qvalidator.html#validate)
        :param proposed_parent_name: The name of the component being considered for assignment as a transform parent
        :param pos: The cursor position in proposed_parent_name. Required to match the QValidator API. Not used.
        """

        # A mapping of component indexes to the indexes of their parents
        parents, fully_mapped = self.populate_parent_mapping(proposed_parent_name)
        if not fully_mapped:
            return QValidator.Invalid

        if self.valid_parent_mapping(parents):
            return QValidator.Acceptable
        else:
            return QValidator.Invalid

    def populate_parent_mapping(self, proposed_parent_name):
        """
        Builds a dictionary that maps component indexes to the indexes of their parents

        :param proposed_parent_name: The name of the component being considered as a parent for the component at this
        validators index
        :returns: The mapping, and a boolean indicating if the mapping was fully populated
        """
        mapping = {}
        # Build the parents mapping, including the mapping that would be set by the new assignment
        candidate_parent_index = -1
        for component in self.list_model.components:
            index = self.list_model.components.index(component)
            if component.transform_parent is None:
                parent_index = 0
            else:
                parent_index = self.list_model.components.index(
                    component.transform_parent
                )
            mapping[index] = parent_index
            if component.name == proposed_parent_name:
                candidate_parent_index = index
        if candidate_parent_index == -1:
            # input is not a valid parent name
            return mapping, False
        mapping[self.model_index] = candidate_parent_index
        return mapping, True

    def valid_parent_mapping(self, parents):
        """
        Explores a parent id mapping dictionary from the validators index to determine if it's valid

        A valid parent hierarchy is one that ends in a component being its own parent.
        The validationFailed signal is emitted if a circular dependency is found.
        :param parents: A mapping of component indexes to the indexes of their parent
        :return: A boolean indicating if the component at the validators index has a valid parent hierarchy
        """
        visited = {self.model_index}
        index = self.model_index
        # Explore the parent mapping as a graph until all connections have been explored or a loop is found
        for _ in range(len(parents)):
            parent_index = parents[index]
            if parent_index == index:
                # self looping, acceptable end of tree
                return True
            if parent_index in visited:
                # loop found
                self.validation_failed.emit()
                return False
            visited.add(parent_index)
            index = parent_index
        # A result should have been found in the loop. Fail the validation
        return False


class NameValidator(ValidatorOnListModel):
    """
    Validator to ensure item names are unique within a model that has a 'name' property

    The validationFailed signal is emitted if an entered name is not unique.
    """

    def __init__(self):
        super().__init__()

    def validate(self, input: str, pos: int):
        if not input:
            self.is_valid.emit(False)
            return QValidator.Intermediate
        name_role = Qt.DisplayRole
        for role, name in self.list_model.roleNames().items():
            if name == b"name":
                name_role = role
                break
        for i in range(self.list_model.rowCount()):
            if i != self.model_index:
                index = self.list_model.createIndex(i, 0)
                name_at_index = self.list_model.data(index, name_role)
                if name_at_index == input:
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

        :param file_types:
        """
        super().__init__()
        self.file_types = file_types

    def validate(self, input: str, pos: int):
        if not input:
            self.is_valid.emit(False)
            return QValidator.Intermediate
        if not os.path.isfile(input):
            self.is_valid.emit(False)
            return QValidator.Intermediate
        for suffixes in GEOMETRY_FILE_TYPES.values():
            for suff in suffixes:
                if input.endswith(f".{suff}"):
                    self.is_valid.emit(True)
                    return QValidator.Acceptable
        self.is_valid.emit(False)
        return QValidator.Invalid

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
        print("Name: {}".format(self.name_is_valid))
        self.validate_ok()

    def set_file_valid(self, is_valid):
        self.file_is_valid = is_valid
        print("File: {}".format(self.file_is_valid))
        self.validate_ok()

    def set_units_valid(self, is_valid):
        self.units_are_valid = is_valid
        print("Units: {}".format(self.units_are_valid))
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

        print("Is valid {}".format(unacceptable))
        self.is_valid.emit(not any(unacceptable))

    # Signal to indicate that the fields are valid or invalid. False: invalid.
    is_valid = Signal(bool)
