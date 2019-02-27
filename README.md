[![License (2-Clause BSD)](https://img.shields.io/badge/license-BSD%202--Clause-blue.svg)](https://github.com/ess-dmsc/nexus-constructor/blob/master/LICENSE) [![codecov](https://codecov.io/gh/ess-dmsc/nexus-constructor/branch/master/graph/badge.svg)](https://codecov.io/gh/ess-dmsc/nexus-constructor) [![Build Status](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-constructor/job/master/badge/icon)](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-constructor/job/master/)

# nexus-constructor
Construct NeXus files with instrument geometry information using a GUI

## Installing dependencies

This project is developed for Python 3.6, so an install of 3.6 or higher
is required. https://www.python.org/downloads/

Python dependencies are listed in requirements.txt at the root of the
repository. They can be installed from a terminal by running
`pip install -r requirements.txt`

The black pre-commit hook (installed by [pre-commit](https://pre-commit.com/)) requires Python 3.6 or above.

## Running the application

Run the python script `main.py` located in the root of the repository.

## Running unit tests

Unit tests are written to use [pytest](https://docs.pytest.org/en/latest/).
Once the dependencies have been installed, they can be run from a terminal in
the project's root directory by running the command `pytest`.

Test coverage can be checked by running the following from the root of the repository:
```
pytest --cov=nexus_constructor
```

## Linter

flake8 is used to check [pep8](https://www.python.org/dev/peps/pep-0008/?) 
compliance. It is installed via pip and can be run as `flake8` in the project's 
root directory. 

## Testing the UI

A script for testing the UI's functionality can be found at [tests/UITests.md](tests/UITests.md)

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

see [Developer Notes](DeveloperNotes.md)
