from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QSplitter
from nexus_constructor.instrument_view import InstrumentView


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1287, 712)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setChildrenCollapsible(False)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.addWidget(self.splitter)
        self.gridLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMinimumSize(QtCore.QSize(500, 0))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.componentsTabLayout = QtWidgets.QVBoxLayout()
        self.componentsTabLayout.setObjectName("componentsTabLayout")
        self.componentTreeView = QtWidgets.QTreeView(self.tab_2)
        self.componentTreeView.setObjectName("componentTreeView")
        self.componentsTabLayout.addWidget(self.componentTreeView)
        self.verticalLayout_2.addLayout(self.componentsTabLayout)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(self.tab)
        self.widget.setObjectName("widget")
        self.verticalLayout.addWidget(self.widget)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.splitter.addWidget(self.tabWidget)
        self.sceneWidget = InstrumentView(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sceneWidget.sizePolicy().hasHeightForWidth())
        self.sceneWidget.setSizePolicy(sizePolicy)
        self.sceneWidget.setMinimumSize(QtCore.QSize(745, 0))
        self.sceneWidget.setObjectName("sceneWidget")
        self.splitter.addWidget(self.sceneWidget)
        self.verticalLayout_3.addLayout(self.gridLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1287, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_NeXus_file = QtWidgets.QAction(MainWindow)
        self.actionOpen_NeXus_file.setObjectName("actionOpen_NeXus_file")
        self.actionExport_to_NeXus_file = QtWidgets.QAction(MainWindow)
        self.actionExport_to_NeXus_file.setObjectName("actionExport_to_NeXus_file")
        self.actionExport_to_Filewriter_JSON = QtWidgets.QAction(MainWindow)
        self.actionExport_to_Filewriter_JSON.setObjectName(
            "actionExport_to_Filewriter_JSON"
        )
        self.menuFile.addAction(self.actionOpen_NeXus_file)
        self.menuFile.addAction(self.actionExport_to_NeXus_file)
        self.menuFile.addAction(self.actionExport_to_Filewriter_JSON)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QtWidgets.QApplication.translate(
                "MainWindow", "NeXus Constructor", None, -1
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_2),
            QtWidgets.QApplication.translate("MainWindow", "Components", None, -1),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab),
            QtWidgets.QApplication.translate(
                "MainWindow", "NeXus File Layout", None, -1
            ),
        )
        self.menuFile.setTitle(
            QtWidgets.QApplication.translate("MainWindow", "File", None, -1)
        )
        self.actionOpen_NeXus_file.setText(
            QtWidgets.QApplication.translate("MainWindow", "Open NeXus file", None, -1)
        )
        self.actionExport_to_NeXus_file.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Export to NeXus file", None, -1
            )
        )
        self.actionExport_to_Filewriter_JSON.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Export to Filewriter JSON", None, -1
            )
        )
