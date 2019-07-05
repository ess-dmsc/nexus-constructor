import os
from functools import partial

import h5py
import silx.gui.hdf5
from PySide2.QtWidgets import QDialog, QLabel, QGridLayout, QComboBox, QPushButton

from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.instrument import Instrument
from nexus_constructor.nexus_filewriter_json import writer
from nexus_constructor.ui_utils import file_dialog
from ui.main_window import Ui_MainWindow

NEXUS_FILE_TYPES = {"NeXus Files": ["nxs", "nex", "nx5"]}
JSON_FILE_TYPES = {"JSON Files": ["json", "JSON"]}


class MainWindow(Ui_MainWindow):
    def __init__(self, instrument: Instrument):
        super().__init__()
        self.instrument = instrument

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
        self.treemodel.insertH5pyObject(self.instrument.nexus.nexus_file)
        self.instrument.nexus.file_changed.connect(
            self.update_nexus_file_structure_view
        )
        self.verticalLayout.addWidget(self.widget)
        self.instrument.nexus.show_entries_dialog.connect(self.show_entries_dialog)

        self.instrument.nexus.component_added.connect(self.sceneWidget.add_component)

        self.set_up_warning_window()

        self.widget.setVisible(True)

    def show_entries_dialog(self, map_of_entries: dict, nexus_file: h5py.File):
        """
        Shows the entries dialog when loading a nexus file if there are multiple entries.
        :param map_of_entries: A map of the entry groups, with the key being the name of the group and value being the actual h5py group object.
        :param nexus_file: A reference to the nexus file.
        """
        self.entries_dialog = QDialog()
        self.entries_dialog.setMinimumWidth(400)
        self.entries_dialog.setWindowTitle(
            "Multiple Entries found. Please choose the entry name from the list."
        )
        combo = QComboBox()

        # Populate the combo box with the names of the entry groups.
        [combo.addItem(x) for x in map_of_entries.keys()]

        ok_button = QPushButton()
        ok_button.setText("OK")
        ok_button.clicked.connect(self.entries_dialog.close)

        # Connect the clicked signal of the ok_button to instrument.load_file and pass the file and entry group object.
        ok_button.clicked.connect(
            partial(
                self.instrument.nexus.load_file,
                map_of_entries[combo.currentText()],
                nexus_file,
            )
        )

        self.entries_dialog.setLayout(QGridLayout())
        self.entries_dialog.layout().addWidget(QLabel("Entry:"))
        self.entries_dialog.layout().addWidget(combo)
        self.entries_dialog.layout().addWidget(ok_button)
        self.entries_dialog.show()

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
        if filename:
            with open(filename, "w") as file:
                writer.generate_json(self.instrument, file)

    def open_nexus_file(self):
        filename = file_dialog(False, "Open Nexus File", NEXUS_FILE_TYPES)
        self.instrument.nexus.open_file(filename)

    def show_add_component_window(self):
        self.add_component_window = QDialog()
        self.add_component_window.ui = AddComponentDialog(self.instrument)
        self.add_component_window.ui.setupUi(self.add_component_window)
        self.add_component_window.show()
