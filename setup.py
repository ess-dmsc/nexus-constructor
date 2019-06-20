"""
Build script for producing standalone executables for the python application using cx_freeze.
The output bundles together the python code, libraries and interpreter, along with the app's resources folder.
See https://cx-freeze.readthedocs.io/en/latest/distutils.html for documentation
"""

import sys
import shutil
from pathlib import Path
from cx_Freeze import setup, Executable
import os

# Dependencies are automatically detected, but it struggles with some parts of numpy.
build_exe_options = {
    "packages": ["numpy.core._methods", "numpy.lib.format", "pkg_resources._vendor"],
    "excludes": [
        "pytest",
        "pytest-cov",
        "pytest-qt",
        "PyQt4",
        "tcl",
        "tk",
        "ttk",
        "tkinter",
        "Tkconstants",
        "Tkinter",
        "collections.sys",
        "collections._weakref",
        "notebook",
        "scipy",
        "bokeh",
        "pandas",
        "netCDF4",
        "matplotlib",
        "tables",
        "lxml",
        "fabio",
        "mpl_toolkits",
        "pytz",
        "cryptography",
        "IPython",
        "dask",
        "docutils",
        "distributed",
        "zmq",
        "xarray",
        "PyQt5",
        "babel",
        "sphinx",
    ],
    "bin_includes": ["libssl.so"],
    "include_files": ["ui", "Instrument.schema.json", "definitions"],
}

# GUI applications require a different base on Windows (the default is for a console application).
if sys.platform == "win32":
    base = "Win32GUI"
    removable = []
    extension = ".exe"
else:
    base = None
    removable = []
    extension = ""

larger_folders = [
    "platforms",
    os.path.join("definitions", "manual"),
    "imageformats",
    "mpl-data",
    os.path.join("lib", "PySide2", "Qt", "qml"),
]

setup(
    name="Nexus Constructor",
    version="2.0-pre",
    description="NeXus file constructor with 3D view for components",
    options={"build_exe": build_exe_options},
    executables=[
        Executable("main.py", base=base, targetName="NexusConstructor" + extension)
    ],
)

for file in removable + larger_folders:
    for build_dir in Path(".").glob("build/*"):
        full_path = build_dir / file
        if full_path.exists():
            if full_path.is_dir():
                print("Removing dir: " + str(full_path))
                shutil.rmtree(str(full_path))
            else:
                print("Removing file: " + str(full_path))
                full_path.unlink()
        else:
            print(
                'Path: "' + str(full_path) + '" does not exist, and cannot be deleted'
            )
