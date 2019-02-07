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
```
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
```
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
