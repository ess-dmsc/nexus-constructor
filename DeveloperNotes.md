## Developer Notes

The Nexus Constructor uses a Qt-QML UI through the 'Qt for Python' (aka
'PySide2') bindings. While not as widely used as the PyQt5 library, it is an
official set of bindings produced by Qt, and most existing examples in PyQt5,
can be adapted with fairly little effort. Most methods are also named similarly
enough that c++ examples can be extremely useful too.

### Python and QML

The data classes that internally model an instrument's geometry are found in the
`nexus_constructor.data_model` module. The data that these classes contain is
then exposed to the QML interface through a series of model classes defined in
`nexus_constructor.qml_models`. These models create a set of named
properties, or Roles, that can be read and edited through the QML UI.

For these custom models to be accessible in QML, they need to be registered to a
module. This is done in `nexus_constructor/application.py` alongside the
class that loads the QML files.

To use a custom model and its properties, import its qml module, create an
instance, and use it as the model for a ListView component.
```qml
...
import MyModels 1.0

ListView {
    width: 100; height: 200

    model: InstrumentModel {}
    delegate: Text {
        text: name
    }
}
```

Methods in custom QML/python classes can be made callable using
[slot and signal annotations](https://wiki.qt.io/Qt_for_Python_Signals_and_Slots)

### QML sizing

Each item in QML has two sets of sizing properties.

- `width` and `height` are the actual on screen size of a component in pixels
- `implicitWidth` and `implicitHeight` are the recommended minimum/default size
a component should be in pixels
 
For some components (`Pane` and `Frame`), implicit sizes are calculated
automatically based on their padding values, and their assigned `contentWidth`
and `contentHeight` parameters.
 
Components with a set implicit size can be larger, for instance if they have
been anchored to other components that are wider.
```qml
Rectangle {
    id: rectangle1
    width: 200
}
Rectangle {
    implicitWidth: 100
    anchors.left: rectangle1.left
    anchors.right: rectangle1.right
}
```
A key use of the distinction between the types of width is used in the editor
windows. Each section has its own implicit minimum width. Their container is set
to use the largest implicit width as its actual width, and each component is
then anchored to the sides of the container so that they all appear the same
width.

Were just width properties to be used, a qml binding loop error would occur, as
width would be in a circular dependency with the width of its parent item.

### JSON formats

The NeXus Constructor supports two different json formats, each with a
different purpose.

Nexus Constructor json is designed to mirror the structure of the 
InstrumentModel and data_model classes. Thus it can be used to store and reload
identical representations of the data in them for saving and returning to at a
later time. Its format is defined in `Instrument.schema.json`

Nexus FileWriter json stores an instrument's data in the format required by
[ESS-DMSC's Nexus Filewriter](https://github.com/ess-dmsc/kafka-to-nexus/)
to produce a standard compliant [nexus file](https://www.nexusformat.org/).
As a result, certain transformations are made to the data before it goes into
this format which cannot be reversed, making saving and reloading into the
nexus constructor from this format slightly lossy. This is mostly due to
floating point calculation inaccuracies, but also includes explicitly stating
the dependent transform in a parent if the model was implicitly using the last
one before exporting.

Each format has a package that contains methods for writing and parsing json.
These packages expose the following methods:

 - `generate_json(model: InstrumentModel)`
 produces a json string from the given model
 - `load_json_object_into_instrument_model(json_object: dict, model: InstrumentModel)`
 populates a model with data from a json_object, which can be obtained from the
 load methods in python's `json` package
 
## QML Validators

The `LabeledTextField` is used throughout the QML to allow for user input. These make use of Validators that prevent a user from entering invalid input. The Validators are contained in the `validators.py` file and are tested in `test_validators.py` 

Custom Validators can be created by extending the `QValidator` class and creating a set of checks for user input that may return the following values:
- `Acceptable`
- `Intermediate`
- `Invalid`

### Creating Custom Validators

The Python code for a Validator must be placed in `validator.py`. The example below shows what a custom validator might look like.

```python
class MyCustomValidator(QValidator):
    """
    A custom validator
    """
    def __init__(self):
        super().__init__()
        self.object_used_for_validating_input = AUsefulValidationTool()

    def validate(self, input: str, pos: int):

        valid_input = self.object_used_for_validating_input(input)
        
        if not valid_input:
            self.validationFailure.emit()
            return QValidator.Intermediate
        else:
            self.validationSuccess.emit()
            return QValidator.Acceptable

    validationSuccess = Signal()
    validationFailed = Signal()
```

The constructor can be used for creating any important objects/variables that are used to help validate the input. Note that the signals are declared _outside_ the constructor. Here returning `QValidator.Intermediate` rather than `QValidator.Invalid` prevents our `LabeledTextField` from "freezing" as soon as it receives _any_ valid input.

A test for this validator may then look like

```python
def test_custom_validator():

    custom_validator = MyCustomValidator()

    valid_inputs = [valid1, valid2, ...]
    invalid_inputs = [invalid1, invalid2, ...]

    for input in valid_inputs:
        assert custom_validator.validate(input, 0) == QValidator.Acceptable

    for input in invalid_inputs:
        assert custom_validator.validate(input, 0) == QValidator.Intermediate
```

Once a new validator has been created in Python it must be registered in order for QML to recognise it. This is done by placing some statements in `application.py` similar to the ones below:
```python

from nexus_constructor.validators import MyCustomValidator

qmlRegisterType(MyCustomValidator, 'MyValidators', 1, 0, 'MyCustomValidator')

```

This then makes it possible to access your new custom validator (along with the other validators) by using the following import statement at the top of a QML file:  
`import MyValidators 1.0`.

Once imported, a custom Validator can then be used within a QML field by assigning `validatior: MyCustomValidator`. The example below shows how this is done in the case of the `UnitValidator`.  

```qml
LabeledTextField {
    id: unitInput
    editorText: units
    Layout.fillWidth: true
    anchoredEditor: true
    onEditingFinished: units = editorText

    validator: UnitValidator {
        id: meshUnitValidator
        onValidationFailed: { ValidUnits.validMeshUnits = false }
        onValidationSuccess: { ValidUnits.validMeshUnits = true }
    }
}
```

where `onValidationFailed` and `onValidationSuccess` are custom signals emitted from a `UnitValidator`. As `LabeledTextField` does not 

### Validator Overview

#### UnitValidator


## Adding Geometries

### Unit Conversion

The program enables users to specify a unit of length when adding components. This is implemented with the `pint` library which is capable of taking inputs such as "meter," "metre," "m," etc and recognising that these mean the same thing. This gives the user more leeway when giving units. The conversion is carried out by viewing meters as the default unit of length and multiplying the relevant values by length in meters. For example, loading a geometry in centimeters will result in its points being multiplied by 0.01.