from PySide2.QtWidgets import QDialog, QLabel, QGridLayout
from nexus_constructor.nexus_wrapper import NexusWrapper
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.utils import file_dialog
from ui.main_window import Ui_MainWindow
import silx.gui.hdf5
import os

from nexus_constructor.nexus_filewriter_json import writer

NEXUS_FILE_TYPES = {"NeXus Files": ["nxs", "nex", "nx5"]}
JSON_FILE_TYPES = {"JSON Files": ["json", "JSON"]}


class MainWindow(Ui_MainWindow):
    def __init__(self, nexus_wrapper: NexusWrapper):
        super().__init__()
        self.nexus_wrapper = nexus_wrapper

    def setupUi(self, main_window):
        super().setupUi(main_window)

        self.pushButton.clicked.connect(self.show_add_component_window)
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
        self.treemodel.insertH5pyObject(self.nexus_wrapper.nexus_file)
        self.nexus_wrapper.file_changed.connect(self.update_nexus_file_structure_view)
        self.verticalLayout.addWidget(self.widget)
        self.listView.setModel(self.nexus_wrapper.get_component_list())
        self.nexus_wrapper.set_instrument_view(self.sceneWidget)

        self.set_up_warning_window()

        self.widget.setVisible(True)

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
        self.nexus_wrapper.save_file(filename)

    def save_to_filewriter_json(self):
        filename = file_dialog(True, "Save JSON File", JSON_FILE_TYPES)
        self.nexus_wrapper.save_file(filename)
        if filename:
            with open(filename, "w") as file:
                file.write(
                    writer.generate_json(self.nexus_wrapper.get_component_list())
                )

    def open_nexus_file(self):
        filename = file_dialog(False, "Open Nexus File", NEXUS_FILE_TYPES)
        self.nexus_wrapper.open_file(filename)

    def show_add_component_window(self):
        self.add_window = QDialog()
        self.add_window.ui = AddComponentDialog(self.nexus_wrapper)
        self.add_window.ui.setupUi(self.add_window)
        self.add_window.show()
