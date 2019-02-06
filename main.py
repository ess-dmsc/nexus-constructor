"""
Entry script for the nexus constructor application.
Requires Python 3.5+
"""

import sys
from os import path, environ
from nexus_constructor.application import Application
from PySide2.QtGui import QGuiApplication


location = sys.executable if getattr(sys, 'frozen', False) else __file__
resource_folder = path.join(path.dirname(location), 'resources')

environ['QT_QUICK_CONTROLS_CONF'] = path.join(resource_folder, 'qtquickcontrols2.conf')

app = QGuiApplication(sys.argv)

window = Application(resource_folder)

res = app.exec_()
sys.exit(res)
