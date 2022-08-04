import json
from typing import Dict, List
from weakref import WeakKeyDictionary

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QMessageBox

from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.json.load_from_json import JSONReader
from nexus_constructor.model.component import Component, Group
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
        self.simple_tree_view.triggered.connect(
            lambda: self.on_simple_tree_view(self.simple_tree_view.isChecked())
        )
        self.on_show_action_labels(self.show_action_labels.isChecked())

        self.about_window.triggered.connect(lambda: self.onOpenAboutWindow(AboutWindow))
        # Clear the 3d view when closed
        QApplication.instance().aboutToQuit.connect(self.sceneWidget.delete)
        self._setup_model_signals()
        self.component_tree_view_tab.set_up_model(self.model)
        self._update_views()
        self.simple_tree_view.triggered.emit()

    def _setup_model_signals(self):
        self.model.signals.component_added.connect(self.sceneWidget.add_component)
        self.model.signals.component_removed.connect(self.sceneWidget.delete_component)
        self.model.signals.transformation_changed.connect(
            self._update_transformations_3d_view
        )

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

    def on_simple_tree_view(self, value):
        self.component_tree_view_tab.reset_model()
        self.component_tree_view_tab.component_delegate.use_simple_tree_view(value)

    def show_add_component_dialog(self):
        selected_component = (
            self.component_tree_view_tab.component_tree_view.selectedIndexes()[
                0
            ].internalPointer()
        )
        new_group = Group("", parent_node=selected_component)
        selected_component.children.append(new_group)
        self.show_add_component_window(new_group, new_group=True)

    def show_edit_component_dialog(self):
        selected_component = (
            self.component_tree_view_tab.component_tree_view.selectedIndexes()[
                0
            ].internalPointer()
        )
        self.show_add_component_window(selected_component, False)

    def save_to_filewriter_json(self):
        filename = file_dialog(True, "Save File writer JSON File", JSON_FILE_TYPES)

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
                self.model = reader.model
                self._setup_model_signals()
                self._update_views()

    def _update_transformations_3d_view(self):
        self.sceneWidget.clear_all_transformations()
        for component in self.model.get_components():
            if isinstance(component, Component):
                self.sceneWidget.add_transformation(component)

    def _update_views(self):
        self.sceneWidget.clear_all_transformations()
        self.sceneWidget.clear_all_components()
        self.component_tree_view_tab.set_up_model(self.model)
        self._update_3d_view_with_component_shapes()

    def _update_3d_view_with_component_shapes(self):
        for component in self.model.get_components():
            self.sceneWidget.add_component(component)
            self.sceneWidget.add_transformation(component)

    def show_add_component_window(self, group: Group, new_group: bool):
        self.add_component_window = AddComponentDialog(
            self.central_widget,
            self.model,
            self.component_tree_view_tab.component_model,
            group,
            scene_widget=self.sceneWidget,
            initial_edit=new_group,
            nx_classes=self.nx_classes,
            tree_view_updater=self._update_model,
        )
        self.add_component_window.show()

    def _update_model(self):
        self.component_tree_view_tab.set_up_model(self.model)


def show_errors_message(errors: List[str]):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText("Could not save file as structure invalid, see below for details")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.setDetailedText("\n\n".join([f"- {err}" for err in errors]))
    msgBox.exec_()
