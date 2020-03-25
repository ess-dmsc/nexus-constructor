[![License (2-Clause BSD)](https://img.shields.io/badge/license-BSD%202--Clause-blue.svg)](https://github.com/ess-dmsc/nexus-constructor/blob/master/LICENSE) [![codecov](https://codecov.io/gh/ess-dmsc/nexus-constructor/branch/master/graph/badge.svg)](https://codecov.io/gh/ess-dmsc/nexus-constructor) [![Build Status](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-constructor/job/master/badge/icon)](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-constructor/job/master/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

# NeXus Constructor
The NeXus Constructor is used for constructing [NeXus files](https://www.nexusformat.org/), including instrument geometry information.

The application can directly output a NeXus file, or create a [_NeXus structure_, JSON template](https://github.com/ess-dmsc/kafka-to-nexus/blob/master/documentation/commands.md#defining-a-nexus-structure) of the file to send to the [File Writer](https://github.com/ess-dmsc/kafka-to-nexus). The JSON template can include data stream details, such that the File Writer populates the NeXus file it creates with data acquired from the detector and other beamline apparatus during an experiment. 

![NeXus Constructor](resources/images/nc_screenshot.png)

Although the application may be useful to other institutions using NeXus, the NeXus Constructor is being developed as part of the software suite for the [European Spallation Source (ESS)](https://europeanspallationsource.se/). Please see [this (open access) paper](https://iopscience.iop.org/article/10.1088/1748-0221/13/10/T10001) for more information on the ESS software.   

Currently tested on Windows 10, Ubuntu 18.04/19.10 and CentOS 7, it should also work on other Linux distributions. Currently it does not work on Mac due to a bug in Qt, but we hope to resolve this soon.

## Installing dependencies

Binary packages for release versions can be downloaded on the [releases page](https://github.com/ess-dmsc/nexus-constructor/releases), or to run the latest development version please follow the instructions below.

This project is developed for Python 3.6, so an install of 3.6 or higher
is required. https://www.python.org/downloads/

Runtime Python dependencies are listed in requirements.txt at the root of the
repository. They can be installed from a terminal by running
```
pip install -r requirements.txt
```

### Development dependencies

Development dependencies (including all runtime dependencies) can be installed by using the following command: 

```
pip install -r requirements-dev.txt
```

The black pre-commit hook (installed by [pre-commit](https://pre-commit.com/)) requires Python 3.6 or above.
You need to once run
```
pre-commit install
```
to activate the pre-commit check.

## Usage

Run the python script `nexus-constructor.py` located in the root of the repository.

## Developer Documentation

See the [Wiki](https://github.com/ess-dmsc/nexus-constructor/wiki/Developer-Notes) for developer documentation.
