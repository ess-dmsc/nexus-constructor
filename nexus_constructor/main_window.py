import json
from typing import Dict, List, Optional
from weakref import WeakKeyDictionary

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox

from nexus_constructor.add_component_window import AddComponentDialog
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
        self.open_json_file_action.triggered.connect(self.open_json_file)
        self.export_to_filewriter_JSON_action.triggered.connect(
            self.save_to_filewriter_json
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

    def on_show_action_labels(self, value):
        self.component_tree_view_tab.component_tool_bar.setToolButtonStyle(
            Qt.ToolButtonTextUnderIcon if value else Qt.ToolButtonIconOnly
        )

    def show_edit_component_dialog(self):
        selected_component = (
            self.component_tree_view_tab.component_tree_view.selectedIndexes()[
                0
            ].internalPointer()
        )
        self.show_add_component_window(selected_component)

    def save_to_filewriter_json(self):
        filename = file_dialog(True, "Save Filewriter JSON File", JSON_FILE_TYPES)

        if filename:
            if not filename.endswith(".json"):
                filename += ".json"
            error_collector: List[str] = []
            data_dump = json.dumps(self.model.as_dict(error_collector), indent=2)
            if error_collector:
                show_errors_message(error_collector)
                return
            with open(filename, "w") as file:
                file.write(data_dump)

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
                self.model.entry = reader.model.entry
                self._update_views()

    def _update_transformations_3d_view(self):
        self.sceneWidget.clear_all_transformations()
        for component in self.model.entry.instrument.get_components():
            self.sceneWidget.add_transformation(component.name, component.qtransform)

    def _update_views(self):
        self.sceneWidget.clear_all_transformations()
        self.sceneWidget.clear_all_components()
        self.component_tree_view_tab.set_up_model(self.model)
        self._update_3d_view_with_component_shapes()

    def _update_3d_view_with_component_shapes(self):
        for component in self.model.entry.instrument.get_components():
            shape, positions = component.shape
            self.sceneWidget.add_component(
                component.name, component.nx_class, shape, positions
            )
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


def show_errors_message(errors: List[str]):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText("Could not save file as structure invalid, see below for details")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.setDetailedText("\n\n".join([f"- {err}" for err in errors]))
    msgBox.exec_()


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
        quit_msg = "Do you want to close the component editor?"
        reply = QMessageBox.question(
            self,
            "Really quit?",
            quit_msg,
            QMessageBox.Close | QMessageBox.Ignore,
            QMessageBox.Close,
        )
        if reply == QMessageBox.Close:
            event.accept()
        else:
            event.ignore()
