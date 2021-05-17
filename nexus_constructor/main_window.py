import json
import uuid
from typing import Dict, Optional
from weakref import WeakKeyDictionary

from nexusutils.nexusbuilder import NexusBuilder
from PySide2.QtCore import QSettings, Qt
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
)

from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.create_forwarder_config import create_forwarder_config
from nexus_constructor.json.load_from_json import JSONReader
from nexus_constructor.model.component import Component
from nexus_constructor.model.model import Model
from nexus_constructor.ui_utils import file_dialog, show_warning_dialog
from ui.main_window import Ui_MainWindow

from .about_window import AboutWindow

NEXUS_FILE_TYPES = {"NeXus Files": ["nxs", "nex", "nx5"]}
JSON_FILE_TYPES = {"JSON Files": ["json", "JSON"]}
FLATBUFFER_FILE_TYPES = {"FlatBuffer Files": ["flat", "FLAT"]}


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, model: Model, nx_classes: Dict):
        super().__init__()
        self.model = model
        self.nx_classes = nx_classes
        # For book-keeping all registered windows
        self._registered_windows: WeakKeyDictionary = WeakKeyDictionary()

    def setupUi(self, main_window):
        super().setupUi(main_window)

        self.export_to_nexus_file_action.triggered.connect(self.save_to_nexus_file)
        self.open_nexus_file_action.triggered.connect(self.open_nexus_file)
        self.open_json_file_action.triggered.connect(self.open_json_file)
        self.open_idf_file_action.triggered.connect(self.open_idf_file)
        self.export_to_filewriter_JSON_action.triggered.connect(
            self.save_to_filewriter_json
        )
        self.export_to_forwarder_config_action.triggered.connect(
            self.save_to_forwarder_config
        )
        self.show_action_labels.triggered.connect(
            lambda: self.on_show_action_labels(self.show_action_labels.isChecked())
        )
        self.about_window.triggered.connect(lambda: self.onOpenAboutWindow(AboutWindow))
        # Clear the 3d view when closed
        QApplication.instance().aboutToQuit.connect(self.sceneWidget.delete)

        self.model.signals.component_added.connect(self.sceneWidget.add_component)
        self.model.signals.component_removed.connect(self.sceneWidget.delete_component)
        self.component_tree_view_tab.set_up_model(self.model)
        self.model.signals.transformation_changed.connect(
            self._update_transformations_3d_view
        )

        self._set_up_file_writer_control_window(main_window)
        self.file_writer_control_window = None
        self._update_views()

    def onOpenAboutWindow(self, instance):
        if self.checkWindowOpen(instance, self._registered_windows):
            return
        return instance(parent=self)

    def checkWindowOpen(self, instance, windows):
        """Check if window is already open, then bring it to front"""
        for window in windows:
            if isinstance(window, instance):
                window.activateWindow()
                return True
        return False

    def registerWindow(self, instance):
        """Register an instance of a QMainWindow"""
        self._registered_windows[instance] = 1

    def unregisterWindow(self, instance):
        """De-Register an instance if closeEvent is called"""
        if instance in self._registered_windows:
            del self._registered_windows[instance]

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

    def on_show_action_labels(self, value):
        self.component_tree_view_tab.component_tool_bar.setToolButtonStyle(
            Qt.ToolButtonTextUnderIcon if value else Qt.ToolButtonIconOnly
        )

    def show_control_file_writer_window(self):
        if self.file_writer_control_window is None:
            from nexus_constructor.file_writer_ctrl_window import FileWriterCtrl

            self.file_writer_ctrl_window = FileWriterCtrl(
                QSettings("ess", "nexus-constructor")
            )
            self.file_writer_ctrl_window.show()

    def show_edit_component_dialog(self):
        selected_component = (
            self.component_tree_view_tab.component_tree_view.selectedIndexes()[
                0
            ].internalPointer()
        )
        self.show_add_component_window(selected_component)

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

    def save_to_forwarder_config(self):
        filename = file_dialog(
            True, "Save Forwarder FlatBuffer File", FLATBUFFER_FILE_TYPES
        )
        if filename:
            provider_type, ok_pressed = QInputDialog.getItem(
                self,
                "Provider type",
                "Select provider type for PVs",
                ["ca", "pva", "fake"],
                0,
                False,
            )
            if ok_pressed:
                with open(filename, "wb") as flat_file:
                    flat_file.write(
                        create_forwarder_config(
                            self.model,
                            provider_type,
                        )
                    )

    def open_nexus_file(self):
        raise NotImplementedError

    def open_json_file(self):
        filename = file_dialog(False, "Open File Writer JSON File", JSON_FILE_TYPES)
        if filename:
            reader = JSONReader()
            success = reader.load_model_from_json(filename)
            if reader.warnings:
                show_warning_dialog(
                    "\n".join(
                        (json_warning.message for json_warning in reader.warnings)
                    ),
                    "Warnings encountered loading JSON",
                    parent=self,
                )
            if success:
                self.model.entry = reader.entry
                self._update_views()

    def _update_transformations_3d_view(self):
        self.sceneWidget.clear_all_transformations()
        for component in self.model.entry.instrument.component_list:
            self.sceneWidget.add_transformation(component.name, component.qtransform)

    def _update_views(self):
        self.sceneWidget.clear_all_transformations()
        self.sceneWidget.clear_all_components()
        self.component_tree_view_tab.set_up_model(self.model)
        self._update_3d_view_with_component_shapes()

    def _update_3d_view_with_component_shapes(self):
        for component in self.model.entry.instrument.component_list:
            shape, positions = component.shape
            self.sceneWidget.add_component(component.name, shape, positions)
            self.sceneWidget.add_transformation(component.name, component.qtransform)

    def show_add_component_window(self, component: Optional[Component] = None):
        self.add_component_window = QDialogCustom()
        self.add_component_window.ui = AddComponentDialog(
            self.model,
            self.component_tree_view_tab.component_model,
            component,
            nx_classes=self.nx_classes,
            parent=self,
        )
        self.add_component_window.ui.setupUi(self.add_component_window)
        self.add_component_window.show()


class QDialogCustom(QDialog):
    """
    Custom QDialog class that enables the possibility to properly produce
    a message box in the component editor to the users,
    asking if they are sure to quit editing component when exiting.
    """

    def __init__(self):
        super().__init__()
        self._is_accepting_component = True

    def disable_msg_box(self):
        self._is_accepting_component = False

    def close_without_msg_box(self):
        """
        Close widget without producing the message box in closeEvent method.
        """
        self.disable_msg_box()
        self.close()

    def closeEvent(self, event):
        """
        Overriding closeEvent function in the superclass to produce a message box prompting
        the user to exit the add/edit component window. This message box pops up
        when the user exits by pressing the window close (X) button.
        """
        if not self._is_accepting_component:
            event.accept()
            return
        quit_msg = "Are you sure you want to exit the component editor?"
        reply = QMessageBox.question(
            self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
