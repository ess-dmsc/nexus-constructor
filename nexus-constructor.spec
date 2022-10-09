# -*- mode: python ; coding: utf-8 -*-
import PySide6
import os

block_cipher = None

added_files = [
    ("ui/*.png", "ui"),
    ("ui/*.svg", "ui"),
    ("definitions/base_classes/*.nxdl.xml", "definitions/base_classes"),
]

if os.path.isdir(os.path.join(PySide6.__path__[0], "Qt", "plugins", "renderers")):
    added_files.append((
        os.path.join(PySide6.__path__[0], "Qt", "plugins", "renderers"),
        "PySide6/Qt/plugins/renderers",
    ))

# Be careful about removing things from this list.
# Not excluding PyQt5 for example can cause problems if it is installed on your system,
# even if it is not present in the virtualenv you run pyinstaller in.
exclude = [
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
]

a = Analysis(
    ["nexus-constructor.py"],
    pathex=["/home/matt/git/nexus-constructor"],
    binaries=[],
    datas=added_files,
    hiddenimports=["PySide6.QtXml"],
    hookspath=[],
    runtime_hooks=[],
    excludes=exclude,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

excluded_binaries = [
    "QtCharts.abi3.so",
    "QtTextToSpeech.abi3.so",
    "QtRemoteObjects.abi3.so",
    "QtScriptTools.abi3.so",
    "QtQuick.abi3.so",
    "QtQml.abi3.so",
    "QtSql.abi3.so",
    "QtLocation.abi3.so",
    "QtMultimedia.abi3.so",
    "QtSensors.abi3.so",
    "libQt5Help.so.5",
    "libQt5Location.so.5",
    "libQt5Multimedia.so.5",
    "libQt5ScriptTools.so.5",
    "libQt5Bluetooth.so.5",
    "libQt5QuickControls2.so.5",
    "libQt5VirtualKeyboard.so.5",
]

a.binaries = TOC([x for x in a.binaries if x[0] not in excluded_binaries])

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="nexus-constructor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="nexus-constructor",
)
