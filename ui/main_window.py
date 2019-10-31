from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QSplitter
from nexus_constructor.instrument_view import InstrumentView


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")

        MainWindow.resize(1280, 720)
        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setObjectName("centralwidget")

        self.splitter = QSplitter(self.central_widget)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setOpaqueResize(True)

        self.main_grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.main_grid_layout.addWidget(self.splitter)
        self.main_grid_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.main_grid_layout.setObjectName("gridLayout_3")

        self.tab_widget = QtWidgets.QTabWidget(self.central_widget)
        self.tab_widget.setMinimumSize(QtCore.QSize(500, 0))
        self.tab_widget.setObjectName("tabWidget")
        self._set_up_component_tree_view()
        self._set_up_silx_view()
        self.splitter.addWidget(self.tab_widget)

        self._set_up_3d_view()

        MainWindow.setCentralWidget(self.central_widget)

        self._set_up_menus(MainWindow)

        self.retranslateUi(MainWindow)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

    def _set_up_3d_view(self):
        self.sceneWidget = InstrumentView(self.splitter)
        self.sceneWidget.setMinimumSize(QtCore.QSize(600, 0))
        self.sceneWidget.setObjectName("sceneWidget")
        self.splitter.addWidget(self.sceneWidget)

    def _set_up_silx_view(self):
        self.silx_tab = QtWidgets.QWidget()
        self.silx_tab.setObjectName("tab")
        self.silx_tab_layout = QtWidgets.QGridLayout(self.silx_tab)
        self.silx_tab_layout.setObjectName("gridLayout_2")
        self.tab_widget.addTab(self.silx_tab, "")

    def _set_up_component_tree_view(self):
        self.component_tree_view_tab = QtWidgets.QWidget()
        self.component_tree_view_tab.setObjectName("tab_2")
        self.tree_view_layout = QtWidgets.QVBoxLayout(self.component_tree_view_tab)
        self.tree_view_layout.setObjectName("verticalLayout_2")
        self.componentsTabLayout = QtWidgets.QVBoxLayout()
        self.componentsTabLayout.setObjectName("componentsTabLayout")
        self.component_tree_view = QtWidgets.QTreeView(self.component_tree_view_tab)
        self.component_tree_view.setObjectName("componentTreeView")
        self.componentsTabLayout.addWidget(self.component_tree_view)
        self.tree_view_layout.addLayout(self.componentsTabLayout)
        self.tab_widget.addTab(self.component_tree_view_tab, "")

    def _set_up_menus(self, MainWindow):
        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 1280, 720))
        self.menu_bar.setObjectName("menubar")
        self.file_menu = QtWidgets.QMenu(self.menu_bar)
        self.file_menu.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menu_bar)
        self.status_bar = QtWidgets.QStatusBar(MainWindow)
        self.status_bar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.status_bar)
        self.open_nexus_file_action = QtWidgets.QAction(MainWindow)
        self.open_nexus_file_action.setObjectName("actionOpen_NeXus_file")
        self.open_json_file_action = QtWidgets.QAction(MainWindow)
        self.open_json_file_action.setObjectName("actionOpen_JSON_file")
        self.export_to_nexus_file_action = QtWidgets.QAction(MainWindow)
        self.export_to_nexus_file_action.setObjectName("actionExport_to_NeXus_file")
        self.export_to_filewriter_JSON_action = QtWidgets.QAction(MainWindow)
        self.export_to_filewriter_JSON_action.setObjectName(
            "actionExport_to_Filewriter_JSON"
        )
        self.export_to_forwarder_JSON_action = QtWidgets.QAction(MainWindow)
        self.file_menu.addAction(self.open_nexus_file_action)
        self.file_menu.addAction(self.open_json_file_action)
        self.file_menu.addAction(self.export_to_nexus_file_action)
        self.file_menu.addAction(self.export_to_filewriter_JSON_action)
        self.file_menu.addAction(self.export_to_forwarder_JSON_action)
        self.menu_bar.addAction(self.file_menu.menuAction())

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QtWidgets.QApplication.translate(
                "MainWindow", "NeXus Constructor", None, -1
            )
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.component_tree_view_tab),
            QtWidgets.QApplication.translate("MainWindow", "Components", None, -1),
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.silx_tab),
            QtWidgets.QApplication.translate(
                "MainWindow", "NeXus File Layout", None, -1
            ),
        )
        self.file_menu.setTitle(
            QtWidgets.QApplication.translate("MainWindow", "File", None, -1)
        )
        self.open_nexus_file_action.setText(
            QtWidgets.QApplication.translate("MainWindow", "Open NeXus file", None, -1)
        )
        self.open_json_file_action.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Open Filewriter JSON file", None, -1
            )
        )
        self.export_to_nexus_file_action.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Export to NeXus file", None, -1
            )
        )
        self.export_to_filewriter_JSON_action.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Export to Filewriter JSON", None, -1
            )
        )
        self.export_to_forwarder_JSON_action.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Export to Forwarder JSON", None, -1
            )
        )
