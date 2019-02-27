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

The input given to a `LabeledTextField` can be checked before it is accepted by using custom Python _Validators_. We define our Validator classes in `validators.py` and place their tests tested in `test_validators.py`  A Validator may return one of the following three inputs to inform QML if the input should be accepted:
- `Acceptable`
- `Intermediate`
- `Invalid`

An explanation of when to use these different return values can be found [here](https://doc.qt.io/qt-5/qvalidator.html).

### Creating Custom Validators

The example below shows what a custom validator might look like. All Validators must implement a `validate` function where the first argument is the input provided by the user.

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

The constructor can be used for creating any important objects/variables that are used to help validate the input. In addition, a developer may wish to create further helper functions for checking input or import them from elsewhere. In the above example, we return `QValidator.Intermediate` rather than `QValidator.Invalid` as this prevents our `LabeledTextField` from "freezing" as soon as it has _any_ valid input. This can be helpful when the text field has a default value and attempting to replace it with something else causes the input to become invalid. Should a validator return `QValidator.Invalid` in this case, QML will attempt to preserve the default input and effectively freeze the `LabeledTextField`. 

In addition to returning `Acceptable`/`Invalid`/`Intermediate` we also make use of custom signals. Such signals are necessary when you wish to program a response to the user input in QML (such as displaying a message if input is unsuitable). These signals are not always required.

Note that the signals are declared _outside_ the constructor but are still accessed with the `self` prefix.

A test for the custom validator may look like the example below:

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

Once a new validator has been created it must be registered in order for QML to recognise it. This is done by placing some statements in `application.py` similar to the ones below:
```python
from nexus_constructor.validators import MyCustomValidator
qmlRegisterType(MyCustomValidator, 'MyValidators', 1, 0, 'MyCustomValidator')
```

This then makes it possible to access your new custom validator (along with the other validators) by using the following import statement at the top of a QML file:  
```
import MyValidators 1.0
```

Once imported, a custom Validator can then be used within a `LabeledTextField` by using the assignment `validatior: MyCustomValidator`. The example below shows how this is done in the case of a field that checks for valid unit import using the `UnitValidator`.  

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

### Validator Overview

#### UnitValidator

The `UnitValidator` uses the `pint` library to check if a text input matches a valid unit of length. It will return `QValidator.Intermediate` and emit the `ValidationFailed` signal if:
- the input could not be converted to a known unit
- the input is a unit of time/volume/area/etc
- the input has no units and simply consists of a number
- the input has a magnitude other than 1 (e.g. "40 cm")

Some of these inputs are required because `pint` is flexible about what it regards as an acceptable physical quantity object. If given an empty string, `pint` will convert this to `1 dimensionless` instead of throwing an Exception. This behaviour can then cause problems if a `dimensionless` object is allowed to propagate further into the program and be passed to functions that assume it is a length. In light of this, some care may be required when using `pint` for checking lengths as you might assume it will reject inputs that it is actually able to accept. 

If the input passes all of the above checks then the `UnitValidator` will return `QValidator.Acceptable` and emit the `ValidationSuccess` signal.

## Adding Geometries

### Unit Conversion

The program is capable of taking inputs such as "meter," "metre," "m," etc and recognising that these mean the same thing. This gives the user more leeway when giving units. The conversion is carried out by viewing meters as the default unit of length and multiplying the relevant values by length in meters. For example, loading a geometry in centimeters will result in its points being multiplied by 0.01.