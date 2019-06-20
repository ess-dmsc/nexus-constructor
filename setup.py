"""
Build script for producing standalone executables for the python application using cx_freeze.
The output bundles together the python code, libraries and interpreter, along with the app's resources folder.
See https://cx-freeze.readthedocs.io/en/latest/distutils.html for documentation
"""

import sys
import shutil
from pathlib import Path
from cx_Freeze import setup, Executable

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

removable_folders = [
    "lib/apt",
    "lib/asn1crypto",
    "lib/asyncio",
    "lib/notebook",
    "lib/xarray",
    "lib/concurrent",
    "lib/bokeh",
    "lib/bs4",
    "lib/certifi",
    "lib/chardet",
    "lib/click",
    "lib/cloudpickle",
    "lib/cryptography",
    "lib/curses",
    "lib/cftime",
    "lib/dask",
    "lib/dateutil",
    "lib/distributed",
    "lib/docutils",
    "lib/fabio",
    "lib/gi",
    "lib/idna",
    "lib/ipykernel",
    "lib/IPython",
    "lib/ipython_genutils",
    "lib/ipywidgets",
    "lib/jinja2",
    "lib/jupyter_client",
    "lib/jupyter_core",
    "lib/lib2to3",
    "lib/locket",
    "lib/lxml",
    "lib/markupsafe",
    "lib/matplotlib",
    "lib/mpl_toolkits",
    "lib/msgpack",
    "lib/multiprocessing",
    "lib/nbconvert",
    "lib/nbformat",
    "lib/netCDF4",
    "lib/nose",
    "lib/numexpr",
    "lib/packaging",
    "lib/pandas",
    "lib/partd",
    "lib/pbr",
    "lib/pexpect",
    "lib/PIL",
    "lib/prompt_toolkit",
    "lib/psutil",
    "lib/ptyprocess",
    "lib/py",
    "lib/pydoc_data",
    "lib/pygments",
    "lib/pytz",
    "lib/requests",
    "lib/scipy",
    "lib/setuptools",
    "lib/simplejson",
    "lib/sortedcontainers",
    "lib/sqlite3",
    "lib/tables",
    "lib/tblib",
    "lib/testpath",
    "lib/toolz",
    "lib/tornado",
    "lib/traitlets",
    "lib/urllib3",
    "lib/wcwidth",
    "lib/webencodings",
    "lib/xmlrpc",
    "lib/yaml",
    "lib/zict",
    "lib/zmq",
    "lib/coverage",
    "lib/distutils",
    "lib/mock",
    "lib/PyQt5",
    "lib/babel",
    "lib/sphinx",
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

for file in removable + removable_folders:
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
