"""Validators to be used on QML input fields"""
from geometry_constructor.instrument_model import InstrumentModel
from PySide2.QtCore import Property, Signal
from PySide2.QtGui import QValidator, QIntValidator


class NullableIntValidator(QIntValidator):
    def validate(self, input: str, pos: int):
        if input == '':
            return QValidator.Acceptable
        else:
            return super().validate(input, pos)


class ValidatorOnInstrumentModel(QValidator):
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
        self.instrument_model = InstrumentModel()
        self.model_index = -1

    def get_index(self):
        return self.model_index

    def set_index(self, val: int):
        self.model_index = val

    @Signal
    def index_changed(self):
        pass

    myindex = Property(int, get_index, set_index, notify=index_changed)

    def get_model(self):
        return self.instrument_model

    def set_model(self, val: InstrumentModel):
        self.instrument_model = val

    @Signal
    def model_changed(self):
        pass

    model = Property('QVariant', get_model, set_model, notify=model_changed)

    validationFailed = Signal()


class TransformParentValidator(ValidatorOnInstrumentModel):
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
        for component in self.instrument_model.components:
            index = self.instrument_model.components.index(component)
            if component.transform_parent is None:
                parent_index = 0
            else:
                parent_index = self.instrument_model.components.index(component.transform_parent)
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
                self.validationFailed.emit()
                return False
            visited.add(parent_index)
            index = parent_index
        # A result should have been found in the loop. Fail the validation
        return False


class NameValidator(ValidatorOnInstrumentModel):
    """
    Validator to ensure component names are unique within a model

    Names must be unique as they are used to identify component objects in generated NeXus files, which must be named
    uniquely.
    The validationFailed signal is emitted if an entered name is not unique.
    """

    def __init__(self):
        super().__init__()

    def validate(self, input: str, pos: int):
        components = self.instrument_model.components
        # if any other component has the same name, it's invalid for this component
        for component in (components[i] for i in range(len(components)) if i != self.model_index):
            if component.name == input:
                self.validationFailed.emit()
                return QValidator.Invalid
        return QValidator.Acceptable
