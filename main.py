"""
Entry script for the nexus constructor application.
Requires Python 3.5+
"""

import sys
from os import path, environ
from nexus_constructor.application import Application
from PySide2.QtGui import QGuiApplication, QIcon

if __name__ == "__main__":
    location = sys.executable if getattr(sys, "frozen", False) else __file__
    resource_folder = path.join(path.dirname(location), "resources")

    environ["QT_QUICK_CONTROLS_CONF"] = path.join(
        resource_folder, "qtquickcontrols2.conf"
    )

    app = QGuiApplication(sys.argv)

    # Non-blank name and organisation name are required by DefaultFileDialog
    app.setOrganizationName("name")
    app.setOrganizationDomain("domain")
    app.setWindowIcon(QIcon(path.join(resource_folder, "images", "icon.png")))

    window = Application(resource_folder)
    sys.exit(app.exec_())
