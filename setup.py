"""
Build script for producing standalone executables for the python application using cx_freeze.
The output bundles together the python code, libraries and interpreter, along with the app's resources folder.
See https://cx-freeze.readthedocs.io/en/latest/distutils.html for documentation
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it struggles with some parts of numpy.
build_exe_options = {"packages": ["numpy.core._methods",
                                  "numpy.lib.format"],
                     "excludes": ["pytest",
                                  "pytest-cov",
                                  "pytest-qt"
                                  ],
                     "include_files": ["resources"]}

# GUI applications require a different base on Windows (the default is for a console application).
if sys.platform == "win32":
    base = "Win32GUI"
    extension = '.exe'
else:
    base = None
    extension = ''

setup(name="Nexus Geometry Test App",
      version="0.1",
      description="Technology test program for the nexus geometry constructor",
      options={"build_exe": build_exe_options},
      executables=[Executable("main.py", base=base, targetName="NexusGeometry" + extension)])
