from PySide2.QtCore import QMetaObject, QObject, QRect, QSize
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import (
    QAction,
    QGridLayout,
    QLayout,
    QMenu,
    QMenuBar,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QWidget,
)

from nexus_constructor.instrument_view.instrument_view import InstrumentView
from ui.treeview_tab import ComponentTreeViewTab


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.resize(1280, 720)
        self.central_widget = QWidget(MainWindow)

        self.splitter = QSplitter(self.central_widget)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setOpaqueResize(True)

        self.main_grid_layout = QGridLayout(self.central_widget)
        self.main_grid_layout.addWidget(self.splitter)
        self.main_grid_layout.setSizeConstraint(QLayout.SetDefaultConstraint)

        self.tab_widget = QTabWidget(self.central_widget)
        self.tab_widget.setMinimumSize(QSize(500, 0))
        self._set_up_component_tree_view()
        self.splitter.addWidget(self.tab_widget)

        self._set_up_3d_view()

        MainWindow.setCentralWidget(self.central_widget)

        self._set_up_menus(MainWindow)
        self.tab_widget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(MainWindow)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

    def _set_up_3d_view(self):
        self.sceneWidget.setMinimumSize(QSize(600, 0))
        self.splitter.addWidget(self.sceneWidget)

    def _set_up_component_tree_view(self):
        self.sceneWidget = InstrumentView(self.splitter)
        self.component_tree_view_tab = ComponentTreeViewTab(
            scene_widget=self.sceneWidget, parent=self
        )
        self.tab_widget.addTab(self.component_tree_view_tab, "")

    def _set_up_menus(self, MainWindow: QObject):
        self.menu_bar = QMenuBar()
        self.menu_bar.setGeometry(QRect(0, 0, 1280, 720))
        self.file_menu = QMenu(self.menu_bar)
        MainWindow.setMenuBar(self.menu_bar)
        self.status_bar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.status_bar)
        self.new_json_template_action = QAction(MainWindow)
        self.new_json_template_action.setShortcut(QKeySequence("Ctrl+N"))
        self.open_json_file_action = QAction(MainWindow)
        self.open_json_file_action.setShortcut(QKeySequence("Ctrl+O"))
        self.export_to_filewriter_JSON_action = QAction(MainWindow)
        self.export_to_filewriter_JSON_action.setShortcut(QKeySequence("Ctrl+S"))
        self.export_to_compressed_filewriter_JSON_action = QAction(MainWindow)
        self.file_menu.addAction(self.new_json_template_action)
        self.file_menu.addAction(self.open_json_file_action)
        self.file_menu.addAction(self.export_to_filewriter_JSON_action)
        self.file_menu.addAction(self.export_to_compressed_filewriter_JSON_action)

        self.view_menu = QMenu(self.menu_bar)
        self.show_action_labels = QAction(MainWindow)
        self.show_action_labels.setCheckable(True)
        self.show_action_labels.setChecked(True)
        self.simple_tree_view = QAction(MainWindow)
        self.simple_tree_view.setCheckable(True)
        self.about_window = QAction(MainWindow)
        self.view_menu.addAction(self.about_window)
        self.view_menu.addAction(self.show_action_labels)
        self.view_menu.addAction(self.simple_tree_view)

        self.menu_bar.addAction(self.file_menu.menuAction())
        self.menu_bar.addAction(self.view_menu.menuAction())
        self._set_up_titles(MainWindow)

    def _set_up_titles(self, MainWindow):
        MainWindow.setWindowTitle("NeXus Constructor")
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.component_tree_view_tab), "Nexus Structure"
        )
        self.file_menu.setTitle("File")
        self.new_json_template_action.setText("Create new NeXus JSON template")
        self.open_json_file_action.setText("Open File writer JSON file")
        self.export_to_filewriter_JSON_action.setText("Export to file writer JSON")
        self.export_to_compressed_filewriter_JSON_action.setText(
            "Export to compressed file writer JSON"
        )

        self.view_menu.setTitle("View")
        self.show_action_labels.setText("Show Button Labels")
        self.simple_tree_view.setText("Use Simple Tree Model View")
        self.about_window.setText("About")

        self.menu_bar.setNativeMenuBar(False)
