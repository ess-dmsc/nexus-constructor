import os.path as osp

from PySide2.QtGui import QFont
from PySide2.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


class AboutWindow(QMainWindow):
    """AboutWindow class"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("About")

        if parent is not None:
            parent.registerWindow(self)

        background_image = osp.join(
            osp.dirname(osp.abspath(__file__)), "../ui/icon.png"
        )

        self._central_widget = QWidget()
        self._central_widget.setFont(QFont("monospace", pointSize=11))
        self._central_widget.setStyleSheet(
            f"background-image:url({background_image});"
            "background-position:center; background-repeat:no-repeat;"
        )

        self.setCentralWidget(self._central_widget)
        self.setupUi()
        self.setFixedSize(660, 450)
        self.show()

    def setupUi(self):
        layout = QVBoxLayout()

        name = QLabel("Nexus-constructor")
        name.setFont(QFont("Helvetica", pointSize=32, weight=75))

        url = (
            "https://github.com/ess-dmsc/nexus-constructor/blob/main/getting_started.md"
        )
        getting_started = QLabel(f"<a href={url}>Getting Started</a>")
        getting_started.setFont(QFont("monospace", pointSize=14))
        getting_started.setOpenExternalLinks(True)

        copyright = QLabel(
            "Copyright (c) 2018, European Spallation Source - Data Management & Software Centre"
            "\nAll rights reserved."
        )
        copyright.setFont(QFont("monospace", pointSize=10))

        layout.addWidget(name)
        layout.addStretch(10)
        layout.addWidget(getting_started)
        layout.addWidget(copyright)
        self._central_widget.setLayout(layout)

    def closeEvent(self, QCloseEvent):
        if self.parent() is not None:
            self.parent().unregisterWindow(self)
        super().closeEvent(QCloseEvent)
