[![License (2-Clause BSD)](https://img.shields.io/badge/license-BSD%202--Clause-blue.svg)](https://github.com/ess-dmsc/nexus-geometry-constructor/blob/master/LICENSE) [![codecov](https://codecov.io/gh/ess-dmsc/nexus-geometry-constructor/branch/master/graph/badge.svg)](https://codecov.io/gh/ess-dmsc/nexus-geometry-constructor) [![Build Status](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-geometry-constructor/job/master/badge/icon)](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-geometry-constructor/job/master/)

# nexus-geometry-constructor
Construct NeXus files with instrument geometry information using a GUI

## Installing dependencies

This project is developed for Python 3.5, so an install of 3.5 or higher
is required. https://www.python.org/downloads/

Python dependencies are listed in requirements.txt at the root of the
repository. They can be installed from a terminal by running
`pip install -r requirements.txt`

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
