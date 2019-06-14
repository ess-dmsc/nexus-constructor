#ui/

This directory contains auto-generated python files and UI files to be used with Qt Creator/Qt Designer.

Use `pyside2-uic uifile.ui -o pythonfile.py` to convert the .ui files to python with the same name.


## Known issues when using pyside2-uic 
Some of the UI components don't seem to generate the correct import statements when using `pyside2-uic`. They paste the incorrect import statement underneath the code for some reason.


- [QWebEngine](https://bugreports.qt.io/browse/PYSIDE-1020)
  - workaround - paste in  `from PySide2.QtWebEngineWidgets import QWebEngineView` and remove the incorrect import statement
