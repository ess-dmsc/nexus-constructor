[![License (2-Clause BSD)](https://img.shields.io/badge/license-BSD%202--Clause-blue.svg)](https://github.com/ess-dmsc/nexus-constructor/blob/master/LICENSE) [![codecov](https://codecov.io/gh/ess-dmsc/nexus-constructor/branch/master/graph/badge.svg)](https://codecov.io/gh/ess-dmsc/nexus-constructor) [![Build Status](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-constructor/job/master/badge/icon)](https://jenkins.esss.dk/dm/job/ess-dmsc/job/nexus-constructor/job/master/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

# NeXus Constructor
The NeXus Constructor is used for constructing [NeXus files](https://www.nexusformat.org/) with instrument geometry information using a GUI. It does this by treating everything with an `NX_class` as a component which can contain properties relevant to their respective devices, including position information and component-specific fields.

The Constructor can also be used to output and send run start and stop messages to the [File-Writer](https://github.com/ess-dmsc/kafka-to-nexus) to configure a template of the instrument information for data aggregation.

The file-writer uses streams from the [Apache Kafka](https://kafka.apache.org/) streaming platform to aggregate experiment data which need to be configured by the constructor before use. This is typically dynamic data which may change during an experiment run, such as a motor's position. 

![NeXus Constructor](resources/images/nc_screenshot.png)

Currently tested on Windows 10, Ubuntu 18.04/19.10 and CentOS 7, it should also work on other Linux distributions. Currently it does not work on Mac due to a bug in Qt, but we hope to resolve this soon.

## Installing dependencies

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

## Running the application

Run the python script `nexus-constructor.py` located in the root of the repository.

## Developer Documentation

See the [Wiki](https://github.com/ess-dmsc/nexus-constructor/wiki/Developer-Notes) for developer documentation.
