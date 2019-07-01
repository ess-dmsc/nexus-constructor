from PySide2.QtWidgets import QDialog, QLabel, QGridLayout, QAction, QToolBar
from PySide2.QtGui import QIcon
from nexus_constructor.instrument import Instrument
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.ui_utils import file_dialog
from ui.main_window import Ui_MainWindow
import silx.gui.hdf5
import os

from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.component_tree_view import ComponentEditorDelegate
from nexus_constructor.nexus_filewriter_json import writer

NEXUS_FILE_TYPES = {"NeXus Files": ["nxs", "nex", "nx5"]}
JSON_FILE_TYPES = {"JSON Files": ["json", "JSON"]}


class MainWindow(Ui_MainWindow):
    def __init__(self, instrument: Instrument):
        super().__init__()
        self.instrument = instrument

    def setupUi(self, main_window):
        super().setupUi(main_window)

        self.actionExport_to_NeXus_file.triggered.connect(self.save_to_nexus_file)
        self.actionOpen_NeXus_file.triggered.connect(self.open_nexus_file)
        self.actionExport_to_Filewriter_JSON.triggered.connect(
            self.save_to_filewriter_json
        )

        self.widget = silx.gui.hdf5.Hdf5TreeView()
        self.widget.setAcceptDrops(True)
        self.widget.setDragEnabled(True)
        self.treemodel = self.widget.findHdf5TreeModel()
        self.treemodel.setDatasetDragEnabled(True)
        self.treemodel.setFileDropEnabled(True)
        self.treemodel.setFileMoveEnabled(True)
        self.treemodel.insertH5pyObject(self.instrument.nexus.nexus_file)
        self.instrument.nexus.file_changed.connect(
            self.update_nexus_file_structure_view
        )
        self.verticalLayout.addWidget(self.widget)

        self.instrument.nexus.component_added.connect(self.sceneWidget.add_component)

        self.set_up_warning_window()

        self.widget.setVisible(True)

        component_list = self.instrument.get_component_list()
        self.component_model = ComponentTreeModel(component_list)

        self.componentTreeView.setDragEnabled(True)
        self.componentTreeView.setAcceptDrops(True)
        self.componentTreeView.setDropIndicatorShown(True)
        self.componentTreeView.header().hide()
        self.component_delegate = ComponentEditorDelegate(self.componentTreeView)
        self.componentTreeView.setItemDelegate(self.component_delegate)
        self.componentTreeView.setModel(self.component_model)
        self.componentTreeView.updateEditorGeometries()
        self.componentTreeView.updateGeometries()
        self.componentTreeView.updateGeometry()
        self.componentTreeView.clicked.connect(self.on_clicked)

        self.component_tool_bar = QToolBar("Actions", self.tab_2)
        self.new_component_action = QAction(QIcon("ui/new_component.png"), "New component", self.tab_2)
        self.new_component_action.triggered.connect(self.show_add_component_window)
        self.component_tool_bar.addAction(self.new_component_action)
        self.new_translation_action = QAction(QIcon("ui/new_translation.png"), "New translation", self.tab_2)
        self.new_translation_action.setEnabled(False)
        self.component_tool_bar.addAction(self.new_translation_action)
        self.new_rotation_action = QAction(QIcon("ui/new_rotation.png"), "New rotation", self.tab_2)
        self.new_rotation_action.setEnabled(False)
        self.component_tool_bar.addAction(self.new_rotation_action)
        self.duplicate_action = QAction(QIcon("ui/duplicate.png"), "Duplicate", self.tab_2)
        self.component_tool_bar.addAction(self.duplicate_action)
        self.duplicate_action.setEnabled(False)
        self.delete_action = QAction(QIcon("ui/delete.png"), "Delete", self.tab_2)
        self.delete_action.setEnabled(False)
        self.component_tool_bar.addAction(self.delete_action)
        self.componentsTabLayout.insertWidget(0, self.component_tool_bar)

    def on_clicked(self, index):
        indices = self.componentTreeView.selectedIndexes()
        if len(indices) == 0 or len(indices) != 1:
            self.delete_action.setEnabled(False)
            self.duplicate_action.setEnabled(False)
            self.new_rotation_action.setEnabled(False)
            self.new_translation_action.setEnabled(False)
        else:
            self.delete_action.setEnabled(True)
            self.duplicate_action.setEnabled(True)
            self.new_rotation_action.setEnabled(True)
            self.new_translation_action.setEnabled(True)

    def set_up_warning_window(self):
        """
        Sets up the warning dialog that is shown when the definitions submodule has not been cloned.
        :return:
        """
        definitions_dir = os.path.join(os.curdir, "definitions")

        # Will contain .git even if missing so check that it does not contain just that file.
        if not os.path.exists(definitions_dir) or len(os.listdir(definitions_dir)) <= 1:
            self.warning_window = QDialog()
            self.warning_window.setWindowTitle("NeXus definitions missing")
            self.warning_window.setLayout(QGridLayout())
            self.warning_window.layout().addWidget(
                QLabel(
                    "Warning: NeXus definitions are missing. Did you forget to clone the submodules?\n run git submodule update --init "
                )
            )
            # Set add component button to disabled, as it wouldn't work without the definitions.
            self.pushButton.setEnabled(False)
            self.warning_window.show()

    def update_nexus_file_structure_view(self, nexus_file):
        self.treemodel.clear()
        self.treemodel.insertH5pyObject(nexus_file)

    def save_to_nexus_file(self):
        filename = file_dialog(True, "Save Nexus File", NEXUS_FILE_TYPES)
        self.instrument.nexus.save_file(filename)

    def save_to_filewriter_json(self):
        filename = file_dialog(True, "Save JSON File", JSON_FILE_TYPES)
        self.instrument.nexus.save_file(filename)
        if filename:
            with open(filename, "w") as file:
                file.write(writer.generate_json(self.instrument.get_component_list()))

    def open_nexus_file(self):
        filename = file_dialog(False, "Open Nexus File", NEXUS_FILE_TYPES)
        self.instrument.nexus.open_file(filename)

    def show_add_component_window(self):
        self.add_component_window = QDialog()
        self.add_component_window.ui = AddComponentDialog(self.instrument)
        self.add_component_window.ui.setupUi(self.add_component_window)
        self.add_component_window.show()
