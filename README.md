[![License (2-Clause BSD)](https://img.shields.io/badge/license-BSD%202--Clause-blue.svg)](https://github.com/ess-dmsc/nexus-geometry-constructor/blob/master/LICENSE) [![codecov](https://codecov.io/gh/ess-dmsc/nexus-geometry-constructor/branch/master/graph/badge.svg)](https://codecov.io/gh/ess-dmsc/nexus-geometry-constructor) [![Build Status](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-geometry-constructor/job/master/badge/icon)](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-geometry-constructor/job/master/)

# nexus-constructor
Construct NeXus files with instrument geometry information using a GUI

## Installing dependencies

This project is developed for Python 3.5, so an install of 3.5 or higher
is required. https://www.python.org/downloads/

Python dependencies are listed in requirements.txt at the root of the
repository. They can be installed from a terminal by running
`pip install -r requirements.txt`

## Running the application

Run the python script `main.py` located in the root of the repository.

## Running unit tests

Unit tests are written to use [pytest](https://docs.pytest.org/en/latest/).
Once the dependencies have been installed, they can be run from a terminal in
the project's root directory by running the command `pytest`.

Test coverage can be checked by running the following from the root of the repository:
```
pytest --cov=geometry_constructor
```

## Linter

flake8 is used to check [pep8](https://www.python.org/dev/peps/pep-0008/?) 
compliance. It is installed via pip and can be run as `flake8` in the project's 
root directory. 

## Testing the UI

A script for testing the UI's functionality can be found at [tests/UI Tests.md](tests/UI Tests.md)

## Building a distributable version

A distributable version of the app, with the required python interpreter and
libraries included can be built using [cx_Freeze](https://cx-freeze.readthedocs.io).
It is included in the project's requirements file, and these must be installed
in order to build the distributable. A build can be run with the following
command in the projects root directory:
```
python setup.py build_exe
```
This will create the executable and copy it's required files to the `build`
subdirectory

cx_Freeze is capable of building distributable versions for Windows, OS X, and
Linux, but can only do so from a machine running that operating system.

## Developer notes

The Nexus Constructor uses a Qt-QML UI through the 'Qt for Python' (aka
'PySide2') bindings. While not as widely used as the PyQt5 library, it is an
official set of bindings produced by Qt, and most existing examples in PyQt5,
can be adapted with fairly little effort. Most methods are also named similarly
enough that c++ examples can be extremely useful too.

### Python and QML

The data classes that internally model an instrument's geometry are found in the
`geometry_constructor.data_model` module. The data that these classes contain is
then exposed to the QML interface through a series of model classes defined in
`geometry_constructor.qml_models`. These models create a set of named
properties, or Roles, that can be read and edited through the QML UI.

For these custom models to be accessible in QML, they need to be registered to a
module. This is done in `geometry_constructor/application.py` alongside the
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

Geometry Constructor json is designed to mirror the structure of the 
InstrumentModel and data_model classes. Thus it can be used to store and reload
identical representations of the data in them for saving and returning to at a
later time. Its format is defined in `Instrument.schema.json`

Nexus FileWriter json stores an instrument's data in the format required by
[ESS-DMSC's Nexus Filewriter](https://github.com/ess-dmsc/kafka-to-nexus/)
to produce a standard compliant [nexus file](https://www.nexusformat.org/).
As a result, certain transformations are made to the data before it goes into
this format which cannot be reversed, making saving and reloading into the
geometry constructor from this format slightly lossy. This is mostly due to
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
