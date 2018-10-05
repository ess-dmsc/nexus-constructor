[![License (2-Clause BSD)](https://img.shields.io/badge/license-BSD%202--Clause-blue.svg)](https://github.com/ess-dmsc/nexus-geometry-constructor/blob/master/LICENSE) [![codecov](https://codecov.io/gh/ess-dmsc/nexus-geometry-constructor/branch/master/graph/badge.svg)](https://codecov.io/gh/ess-dmsc/nexus-geometry-constructor) [![Build Status](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-geometry-constructor/job/master/badge/icon)](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-geometry-constructor/job/master/)

# nexus-geometry-constructor
Construct NeXus files with instrument geometry information using a GUI

## Installing dependencies

This project is developed for Python 3.5, so an install of 3.5 or higher
is required. https://www.python.org/downloads/

Python dependencies are listed in requirements.txt at the root of the
repository. They can be installed from a terminal by running
`pip install -r requirements.txt`

## Running the application

The Nexus Geometry test app is run from the python script `main.py`
located in the root of the repository.

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

## Updating resources.qrc

Documentation for the python Qt resources system can be found
[here](https://doc.qt.io/qtforpython/overviews/resources.html). However, as of
4th October 2018, it is barely adapted from the c++ original, with none of it's
examples being written for python or the PySide2 tools.

For a c++ project, `.qrc` files would be compiled using `qmake` and `rcc`, then
loaded into the program using the `QResource` class. It would appear that the
compiled `.rcc` binary files [can be loaded into python through this method](https://github.com/AlexanderBerx/DynaEditor/blob/638f9c0cdd012e1a057315ea3550f933237f99de/dynaeditor/main.py#L13)
but to do so would require those compiler tools to build the file.

Fortunately there's a workaround in PySide2. Within the python environment's
`lib/site-packages/PySide2` directory is the executable `pyside2-rcc`. This can
compile the resources file to a python script, that when imported into the
program will initialise the properties that were originally specified in the
resource files. Any changes to the resources.qrc or files it references will
not be reflected in the code automatically, so the compiler must be rerun. This
can be done from the repo's root directory with:
```
pyside2-rcc resources/resources.qrc -o geometry_constructor/resources.py
```
