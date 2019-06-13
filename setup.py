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
    "include_files": ["resources", "Instrument.schema.json"],
}

unix_removable = [
    "lib/PySide2/Qt/lib/libQt5WebEngine.so.5",
    "lib/PySide2/Qt/lib/libQt5WebEngineCore.so.5",
    "lib/PySide2/Qt/lib/libQt5WebEngineWidgets.so.5",
    "lib/PySide2/libclang.so.6",
    "lib/PySide2/Qt/resources/",
    "lib/PySide2/Qt/translations/",
    "lib/PySide2/Qt/qml",
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
    "lib/html",
    "lib/html5lib",
    "lib/http",
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
    "lib/apt_pkg.cpython-36m-x86_64-linux-gnu.so",
    "lib/_asyncio.cpython-36m-x86_64-linux-gnu.so",
    "lib/audioop.cpython-36m-x86_64-linux-gnu.so",
    "lib/_bz2.cpython-36m-x86_64-linux-gnu.so",
    "lib/_codecs_cn.cpython-36m-x86_64-linux-gnu.so",
    "lib/_codecs_hk.cpython-36m-x86_64-linux-gnu.so",
    "lib/_codecs_iso2022.cpython-36m-x86_64-linux-gnu.so",
    "lib/_codecs_jp.cpython-36m-x86_64-linux-gnu.so",
    "lib/_codecs_kr.cpython-36m-x86_64-linux-gnu.so",
    "lib/_codecs_tw.cpython-36m-x86_64-linux-gnu.so",
    "lib/coverage",
    "lib/_csv.cpython-36m-x86_64-linux-gnu.so",
    "lib/_curses.cpython-36m-x86_64-linux-gnu.so",
    "lib/_decimal.cpython-36m-x86_64-linux-gnu.so",
    "lib/distutils",
    "lib/_hashlib.cpython-36m-x86_64-linux-gnu.so",
    "lib/kiwisolver.cpython-36m-x86_64-linux-gnu.so",
    "lib/libssl.so.1.1",
    "lib/_lsprof.cpython-36m-x86_64-linux-gnu.so",
    "lib/_lzma.cpython-36m-x86_64-linux-gnu.so",
    "lib/mmap.cpython-36m-x86_64-linux-gnu.so",
    "lib/mock",
    "lib/_multibytecodec.cpython-36m-x86_64-linux-gnu.so",
    "lib/_multiprocessing.cpython-36m-x86_64-linux-gnu.so",
    "lib/netifaces.cpython-36m-x86_64-linux-gnu.so",
    "lib/_opcode.cpython-36m-x86_64-linux-gnu.so",
    "lib/readline.cpython-36m-x86_64-linux-gnu.so",
    "lib/resource.cpython-36m-x86_64-linux-gnu.so",
    "lib/setproctitle.cpython-36m-x86_64-linux-gnu.so",
    "lib/_sqlite3.cpython-36m-x86_64-linux-gnu.so",
    "lib/_ssl.cpython-36m-x86_64-linux-gnu.so",
    "lib/termios.cpython-36m-x86_64-linux-gnu.so",
    "lib/_yaml.cpython-36m-x86_64-linux-gnu.so",
    "lib/numpy/f2py",
    "lib/numpy/distutils",
    "lib/PyQt5",
    "lib/PySide2/QtWebChannel.abi3.so",
    "lib/PySide2/QtWebChannel.pyi",
    "lib/PySide2/QtWebEngine.abi3.so",
    "lib/PySide2/QtWebEngineCore.abi3.so",
    "lib/PySide2/QtWebEngineCore.pyi",
    "lib/PySide2/QtWebEngine.pyi",
    "lib/PySide2/QtWebEngineWidgets.abi3.so",
    "lib/PySide2/QtWebEngineWidgets.pyi",
    "lib/PySide2/QtWebSockets.abi3.so",
    "lib/PySide2/QtWebSockets.pyi",
    "lib/PySide2/QtMultimedia.abi3.so",
    "lib/PySide2/QtMultimedia.pyi",
    "lib/PySide2/QtMultimediaWidgets.abi3.so",
    "lib/PySide2/QtMultimediaWidgets.pyi",
    "lib/PySide2/QtTextToSpeech.abi3.so",
    "lib/PySide2/QtTextToSpeech.pyi",
    "lib/PySide2/examples",
    "lib/PySide2/glue",
    "lib/PySide2/include",
]

win_removable = [
    "lib/PySide2/Qt5WebEngine.dll",
    "lib/PySide2/Qt5WebEngineCore.dll",
    "lib/PySide2/Qt5WebEngineWidgets.dll",
    "lib/PySide2/libclang.dll",
    "lib/PySide2/resources/",
    "lib/PySide2/translations/",
    "lib/PySide2/qml",
]

# GUI applications require a different base on Windows (the default is for a console application).
if sys.platform == "win32":
    base = "Win32GUI"
    removable = win_removable
    extension = ".exe"
else:
    base = None
    removable = unix_removable
    extension = ""

setup(
    name="Nexus Constructor",
    version="2.0-pre",
    description="NeXus file constructor with 3D view for components",
    options={"build_exe": build_exe_options},
    executables=[
        Executable("main.py", base=base, targetName="NexusConstructor" + extension)
    ],
)

for file in removable:
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
