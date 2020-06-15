import uuid
from typing import Dict
import json

import h5py
import silx.gui.hdf5
from PySide2.QtCore import QSettings
from PySide2.QtWidgets import QDialog, QLabel, QGridLayout, QComboBox, QPushButton
from PySide2.QtWidgets import QMainWindow, QApplication, QAction, QMessageBox
from nexusutils.nexusbuilder import NexusBuilder

from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.model.component import Component
from nexus_constructor.ui_utils import file_dialog, show_warning_dialog
from nexus_constructor.model.model import Model
from ui.main_window import Ui_MainWindow


NEXUS_FILE_TYPES = {"NeXus Files": ["nxs", "nex", "nx5"]}
JSON_FILE_TYPES = {"JSON Files": ["json", "JSON"]}


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, model: Model, nx_classes: Dict):
        super().__init__()
        self.model = model
        self.nx_classes = nx_classes

    def setupUi(self, main_window):
        super().setupUi(main_window)

        self.export_to_nexus_file_action.triggered.connect(self.save_to_nexus_file)
        self.open_nexus_file_action.triggered.connect(self.open_nexus_file)
        self.open_json_file_action.triggered.connect(self.open_json_file)
        self.open_idf_file_action.triggered.connect(self.open_idf_file)
        self.export_to_filewriter_JSON_action.triggered.connect(
            self.save_to_filewriter_json
        )
        self.export_to_forwarder_JSON_action.triggered.connect(
            self.save_to_forwarder_json
        )

        # Clear the 3d view when closed
        QApplication.instance().aboutToQuit.connect(self.sceneWidget.delete)

        self.widget = silx.gui.hdf5.Hdf5TreeView()
        self.widget.setAcceptDrops(True)
        self.widget.setDragEnabled(True)
        # self.treemodel = self.widget.findHdf5TreeModel()
        # self.treemodel.setDatasetDragEnabled(True)
        # self.treemodel.setFileDropEnabled(True)
        # self.treemodel.setFileMoveEnabled(True)
        # self.treemodel.insertH5pyObject(self.model.signals.nexus_file)
        self.model.signals.file_changed.connect(self.update_nexus_file_structure_view)
        self.silx_tab_layout.addWidget(self.widget)
        # self.model.signals.show_entries_dialog.connect(self.show_entries_dialog)

        self.model.signals.component_added.connect(self.sceneWidget.add_component)
        self.model.signals.component_removed.connect(self.sceneWidget.delete_component)
        self.component_tree_view_tab.set_up_model(self.model)
        self.model.signals.transformation_changed.connect(
            self._update_transformations_3d_view
        )

        self.widget.setVisible(True)

        self._set_up_file_writer_control_window(main_window)
        self.file_writer_control_window = None
        self._update_views()

    def _set_up_file_writer_control_window(self, main_window):
        try:
            import confluent_kafka  # noqa: F401

            self.control_file_writer_action = QAction(main_window)
            self.control_file_writer_action.setText("Control file-writer")
            self.file_menu.addAction(self.control_file_writer_action)
            self.control_file_writer_action.triggered.connect(
                self.show_control_file_writer_window
            )
        except ImportError:
            pass

    def show_control_file_writer_window(self):
        if self.file_writer_control_window is None:
            from nexus_constructor.file_writer_ctrl_window import FileWriterCtrl

            self.file_writer_ctrl_window = FileWriterCtrl(
                self.model, QSettings("ess", "nexus-constructor")
            )
            self.file_writer_ctrl_window.show()

    def show_edit_component_dialog(self):
        selected_component = self.component_tree_view_tab.component_tree_view.selectedIndexes()[
            0
        ].internalPointer()
        self.show_add_component_window(selected_component)

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

        def _load_current_entry():
            self.model.signals.load_file(
                map_of_entries[combo.currentText()], nexus_file
            )
            self._update_views()

        # Connect the clicked signal of the ok_button to signals.load_file and pass the file and entry group object.
        ok_button.clicked.connect(_load_current_entry)

        self.entries_dialog.setLayout(QGridLayout())

        self.entries_dialog.layout().addWidget(QLabel("Entry:"))
        self.entries_dialog.layout().addWidget(combo)
        self.entries_dialog.layout().addWidget(ok_button)
        self.entries_dialog.show()

    def update_nexus_file_structure_view(self, nexus_file):
        self.treemodel.clear()
        self.treemodel.insertH5pyObject(nexus_file)

    def save_to_nexus_file(self):
        filename = file_dialog(True, "Save Nexus File", NEXUS_FILE_TYPES)
        self.model.signals.save_file(filename)

    def open_idf_file(self):
        filename = file_dialog(False, "Open IDF file", {"IDF files": ["xml"]})
        self._load_idf(filename)

    def _load_idf(self, filename):
        try:
            builder = NexusBuilder(
                str(uuid.uuid4()),
                idf_file=filename,
                file_in_memory=True,
                nx_entry_name="entry",
            )
            builder.add_instrument_geometry_from_idf()
            self.model.signals.load_nexus_file(builder.target_file)
            self._update_views()
            QMessageBox.warning(
                self,
                "Mantid IDF loaded",
                "Please manually check the instrument for accuracy.",
            )
        except Exception:
            QMessageBox.critical(self, "IDF Error", "Error whilst loading IDF file")

    def save_to_filewriter_json(self):
        filename = file_dialog(True, "Save Filewriter JSON File", JSON_FILE_TYPES)

        if filename:
            with open(filename, "w") as file:
                json.dump(self.model.as_dict(), file, indent=2)

    def save_to_forwarder_json(self):
        raise NotImplementedError
        # filename = file_dialog(True, "Save Forwarder JSON File", JSON_FILE_TYPES)
        # if filename:
        #     provider_type, ok_pressed = QInputDialog.getItem(
        #         None,
        #         "Provider type",
        #         "Select provider type for PVs",
        #         ["ca", "pva"],
        #         0,
        #         False,
        #     )
        #     default_broker, ok_pressed = QInputDialog.getText(
        #         None,
        #         "Default broker",
        #         "Default Broker: (This will only be used for streams that do not already have a broker)",
        #         text="broker:port",
        #         echo=QLineEdit.Normal,
        #     )
        #     if ok_pressed:
        #         with open(filename, "w") as file:
        #             nexus_constructor.json.forwarder_json_writer.generate_forwarder_command(
        #                 file,
        #                 self.model.signals.entry,
        #                 provider_type=provider_type,
        #                 default_broker=default_broker,
        #             )

    def open_nexus_file(self):
        raise NotImplementedError
        # filename = file_dialog(False, "Open Nexus File", NEXUS_FILE_TYPES)
        # existing_file = self.model.signals.nexus_file
        # if self.model.signals.open_file(filename):
        #     self._update_views()
        #     existing_file.close()

    def open_json_file(self):
        filename = file_dialog(False, "Open File Writer JSON File", JSON_FILE_TYPES)
        if filename:
            with open(filename, "r") as json_file:
                json_data = json_file.read()

                try:
                    json.loads(json_data)
                except ValueError as exception:
                    show_warning_dialog(
                        "Provided file not recognised as valid JSON",
                        "Invalid JSON",
                        f"{exception}",
                        parent=self,
                    )
                    return

                if self.model.signals.load_json_file(json_data):
                    self._update_views()

    def _update_transformations_3d_view(self):
        self.sceneWidget.clear_all_transformations()
        for component in self.model.entry.instrument.get_component_list():
            self.sceneWidget.add_transformation(component.name, component.qtransform)

    def _update_views(self):
        self.sceneWidget.clear_all_transformations()
        self.sceneWidget.clear_all_components()
        self.component_tree_view_tab.set_up_model(self.model)
        self._update_3d_view_with_component_shapes()

    def _update_3d_view_with_component_shapes(self):
        for component in self.model.entry.instrument.get_component_list():
            shape, positions = component.shape
            self.sceneWidget.add_component(component.name, shape, positions)
            self.sceneWidget.add_transformation(component.name, component.qtransform)

    def show_add_component_window(self, component: Component = None):
        self.add_component_window = QDialog()
        self.add_component_window.ui = AddComponentDialog(
            self.model,
            self.component_tree_view_tab.component_model,
            component,
            nx_classes=self.nx_classes,
            parent=self,
        )
        self.add_component_window.ui.setupUi(self.add_component_window)
        self.add_component_window.show()
