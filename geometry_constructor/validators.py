"""Input validators to be used on QML input fields"""
from geometry_constructor.instrument_model import InstrumentModel
from PySide2.QtCore import Property, Signal
from PySide2.QtGui import QValidator


class ValidatorOnInstrumentModel(QValidator):
    """
    Base class for validators that check an indexed item against other components in an InstrumentModel

    Exposes properties that can be set in QML for the component index, and instrument model.
    In QML these can be set with 'myindex' and 'model'

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


class TransformParentValidator(ValidatorOnInstrumentModel):
    """
    Validator to prevent circular transform parent dependencies being created in an instrument model
    """

    def __init__(self):
        super().__init__()

    def validate(self, input: str, pos: int):
        """
        Validates the input as the name of a component's transform parent to check it won't cause a circular dependency

        (http://doc.qt.io/qt-5/qvalidator.html#validate)
        """
        parents = {}

        candidate_parent_index = -1
        for component in self.instrument_model.components:
            index = self.instrument_model.components.index(component)
            if component.transform_parent is None:
                parent_index = 0
            else:
                parent_index = self.instrument_model.components.index(component.transform_parent)
            parents[index] = parent_index
            if component.name == input:
                candidate_parent_index = index
        if candidate_parent_index == -1:
            # input is not a valid parent name
            return QValidator.Invalid
        parents[self.model_index] = candidate_parent_index

        visited = {self.model_index}
        index = self.model_index
        for _ in range(len(parents)):
            parent_index = parents[index]
            if parent_index == index:
                # self looping, acceptable end of tree
                return QValidator.Acceptable
            if parent_index in visited:
                # loop found
                return QValidator.Invalid
            visited.add(parent_index)
            index = parent_index
        # A result should have been found in the loop. Fail the validation
        return QValidator.Invalid


class NameValidator(ValidatorOnInstrumentModel):
    """
    Validator to ensure component names are unique within a model

    Names must be unique as they are used to identify component objects in generated NeXus files, which must be named
    uniquely.
    """

    def __init__(self):
        super().__init__()

    def validate(self, input: str, pos: int):
        components = self.instrument_model.components
        # if any other component has the same name, it's invalid for this component
        for component in (components[i] for i in range(len(components)) if i != self.model_index):
            if component.name == input:
                return QValidator.Invalid
        return QValidator.Acceptable
