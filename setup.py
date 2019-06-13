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
    "lib/coverage",
    "lib/distutils",
    "lib/mock",
    "lib/PySide2/Qt/resources/",
    "lib/PySide2/Qt/translations/",
    "lib/numpy/f2py",
    "lib/numpy/distutils",
    "lib/PyQt5",
    "lib/PySide2/Qt/qml",
]

pyside_files = [
    "lib/PySide2/libclang.",
    "lib/PySide2/libQt5Concurrent.",
    "lib/PySide2/libQt5Network.",
    "lib/PySide2/libQt5PrintSupport.",
    "lib/PySide2/libQt5OpenGL.",
    "lib/PySide2/libQt5Qml.",
    "lib/PySide2/libQt5Svg.",
    "lib/PySide2/QtWebChannel.",
    "lib/PySide2/QtWebEngine.",
    "lib/PySide2/QtWebEngineCore.",
    "lib/PySide2/QtWebEngineWidgets.",
    "lib/PySide2/QtWebSockets.",
    "lib/PySide2/Qt3DAnimation.",
    "lib/PySide2/Qt3DInput.",
    "lib/PySide2/Qt3DLogic.",
    "lib/PySide2/QtCharts.",
    "lib/PySide2/QtConcurrent.",
    "lib/PySide2/QtDataVisualization.",
    "lib/PySide2/QtHelp.",
    "lib/PySide2/QtLocation.",
]

removable_pyside_unix = []
removable_pyside_win = []

for f in pyside_files:
    removable_pyside_unix.append(f + "so.6")
    removable_pyside_unix.append(f + "so.5")
    removable_pyside_unix.append(f + "abi3.so")
    removable_pyside_unix.append(f + "pyi")
    removable_pyside_win.append(f + "dll")

unix_removable = [
    "lib/PySide2/Qt/lib/libQt5WebEngine.so.5",
    "lib/PySide2/Qt/lib/libQt5WebEngineCore.so.5",
    "lib/PySide2/Qt/lib/libQt5WebEngineWidgets.so.5",
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
    "lib/_csv.cpython-36m-x86_64-linux-gnu.so",
    "lib/_curses.cpython-36m-x86_64-linux-gnu.so",
    "lib/_decimal.cpython-36m-x86_64-linux-gnu.so",
    "lib/_hashlib.cpython-36m-x86_64-linux-gnu.so",
    "lib/kiwisolver.cpython-36m-x86_64-linux-gnu.so",
    "lib/libssl.so.1.1",
    "lib/_lsprof.cpython-36m-x86_64-linux-gnu.so",
    "lib/_lzma.cpython-36m-x86_64-linux-gnu.so",
    "lib/mmap.cpython-36m-x86_64-linux-gnu.so",
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
    "lib/PySide2/QtMultimedia.abi3.so",
    "lib/PySide2/QtMultimedia.pyi",
    "lib/PySide2/QtMultimediaWidgets.abi3.so",
    "lib/PySide2/QtMultimediaWidgets.pyi",
    "lib/PySide2/QtTextToSpeech.abi3.so",
    "lib/PySide2/QtTextToSpeech.pyi",
    "lib/PySide2/examples",
    "lib/PySide2/glue",
    "lib/PySide2/include",
    "lib/PySide2/pyside2-lupdate",
    "lib/PySide2/pyside2-rcc",
    "lib/PySide2/QtLocation.pyi",
    "lib/PySide2/QtNetwork.abi3.so",
    "lib/PySide2/QtNetwork.pyi",
    "lib/PySide2/QtOpenGL.abi3.so",
    "lib/PySide2/QtOpenGL.pyi",
    "lib/PySide2/QtPositioning.abi3.so",
    "lib/PySide2/QtPositioning.pyi",
    "lib/PySide2/QtQml.abi3.so",
    "lib/PySide2/QtQml.pyi",
    "lib/PySide2/QtQuick.abi3.so",
    "lib/PySide2/QtQuick.pyi",
    "lib/PySide2/QtQuickWidgets.abi3.so",
    "lib/PySide2/QtQuickWidgets.pyi",
    "lib/PySide2/QtScxml.abi3.so",
    "lib/PySide2/QtScxml.pyi",
    "lib/PySide2/QtSensors.abi3.so",
    "lib/PySide2/QtSensors.pyi",
    "lib/PySide2/QtSql.abi3.so",
    "lib/PySide2/QtSql.pyi",
    "lib/PySide2/QtSvg.abi3.so",
    "lib/PySide2/QtSvg.pyi",
    "lib/PySide2/QtTest.abi3.so",
    "lib/PySide2/QtTest.pyi",
    "lib/PySide2/QtX11Extras.abi3.so",
    "lib/PySide2/QtX11Extras.pyi",
    "lib/PySide2/QtXmlPatterns.abi3.so",
    "lib/PySide2/QtXmlPatterns.pyi",
    "lib/PySide2/scripts",
    "lib/PySide2/support",
    "lib/PySide2/typesystems",
    "imageformats",
    "platforms",
] + removable_folders + removable_pyside_unix

win_removable = [
    "lib/PySide2/Qt5WebEngine.dll",
    "lib/PySide2/Qt5WebEngineCore.dll",
    "lib/PySide2/Qt5WebEngineWidgets.dll",
] + removable_folders + removable_pyside_win

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
