from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import (
    QToolBar,
    QAbstractItemView,
    QMainWindow,
    QApplication,
    QInputDialog,
)
from PySide2.QtWidgets import QDialog, QLabel, QGridLayout, QComboBox, QPushButton

import silx.gui.hdf5
import os
import h5py

import nexus_constructor.json.forwarder_json_writer
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.filewriter_command_dialog import FilewriterCommandDialog
from nexus_constructor.instrument import Instrument
from nexus_constructor.main_window_utils import (
    create_and_add_toolbar_action,
    set_button_states,
    expand_transformation_list,
    add_transformation,
)
from nexus_constructor.transformation_types import TransformationType
from nexus_constructor.ui_utils import file_dialog, show_warning_dialog
from ui.main_window import Ui_MainWindow
from nexus_constructor.component.component import Component

from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.component_tree_view import ComponentEditorDelegate
from nexus_constructor.json import filewriter_json_writer
from nexus_constructor.json.filewriter_json_reader import json_to_nexus

NEXUS_FILE_TYPES = {"NeXus Files": ["nxs", "nex", "nx5"]}
JSON_FILE_TYPES = {"JSON Files": ["json", "JSON"]}


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, instrument: Instrument, definitions_dir: str):
        super().__init__()
        self.instrument = instrument
        self.definitions_dir = definitions_dir

    def setupUi(self, main_window):
        super().setupUi(main_window)

        self.export_to_nexus_file_action.triggered.connect(self.save_to_nexus_file)
        self.open_nexus_file_action.triggered.connect(self.open_nexus_file)
        self.open_json_file_action.triggered.connect(self.open_json_file)
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
        self.treemodel = self.widget.findHdf5TreeModel()
        self.treemodel.setDatasetDragEnabled(True)
        self.treemodel.setFileDropEnabled(True)
        self.treemodel.setFileMoveEnabled(True)
        self.treemodel.insertH5pyObject(self.instrument.nexus.nexus_file)
        self.instrument.nexus.file_changed.connect(
            self.update_nexus_file_structure_view
        )
        self.silx_tab_layout.addWidget(self.widget)
        self.instrument.nexus.show_entries_dialog.connect(self.show_entries_dialog)

        self.instrument.nexus.component_added.connect(self.sceneWidget.add_component)
        self.instrument.nexus.component_removed.connect(
            self.sceneWidget.delete_component
        )
        self.instrument.nexus.transformation_changed.connect(
            self._update_transformations_3d_view
        )

        self.widget.setVisible(True)

        self._set_up_tree_view()
        self.set_up_warning_window()

    def _set_up_tree_view(self):
        self._set_up_component_model()
        self.component_tree_view.setDragEnabled(True)
        self.component_tree_view.setAcceptDrops(True)
        self.component_tree_view.setDropIndicatorShown(True)
        self.component_tree_view.header().hide()
        self.component_tree_view.updateEditorGeometries()
        self.component_tree_view.updateGeometries()
        self.component_tree_view.updateGeometry()
        self.component_tree_view.clicked.connect(self._set_button_state)
        self.component_tree_view.setSelectionMode(QAbstractItemView.SingleSelection)

        self.component_tool_bar = QToolBar("Actions", self.component_tree_view_tab)
        self.new_component_action = create_and_add_toolbar_action(
            "new_component.png",
            "New Component",
            self.show_add_component_window,
            self.component_tool_bar,
            self.component_tree_view_tab,
            True,
        )
        self.new_translation_action = create_and_add_toolbar_action(
            "new_translation.png",
            "New Translation",
            lambda: self._add_transformation(TransformationType.TRANSLATION),
            self.component_tool_bar,
            self.component_tree_view_tab,
        )
        self.new_rotation_action = create_and_add_toolbar_action(
            "new_rotation.png",
            "New Rotation",
            lambda: self._add_transformation(TransformationType.ROTATION),
            self.component_tool_bar,
            self.component_tree_view_tab,
        )
        self.create_link_action = create_and_add_toolbar_action(
            "create_link.png",
            "Create Link",
            self.on_create_link,
            self.component_tool_bar,
            self.component_tree_view_tab,
        )
        self.duplicate_action = create_and_add_toolbar_action(
            "duplicate.png",
            "Duplicate",
            self.on_duplicate_node,
            self.component_tool_bar,
            self.component_tree_view_tab,
        )
        self.edit_component_action = create_and_add_toolbar_action(
            "edit_component.png",
            "Edit Component",
            self.show_edit_component_dialog,
            self.component_tool_bar,
            self.component_tree_view_tab,
        )
        self.delete_action = create_and_add_toolbar_action(
            "delete.png",
            "Delete",
            self.on_delete_item,
            self.component_tool_bar,
            self.component_tree_view_tab,
        )
        self.zoom_action = create_and_add_toolbar_action(
            "zoom.svg",
            "Zoom To Component",
            self.on_zoom_item,
            self.component_tool_bar,
            self.component_tree_view_tab,
        )
        self.component_tool_bar.insertSeparator(self.zoom_action)
        self.componentsTabLayout.insertWidget(0, self.component_tool_bar)

    def _set_up_component_model(self):
        self.component_model = ComponentTreeModel(self.instrument)
        self.component_delegate = ComponentEditorDelegate(
            self.component_tree_view, self.instrument
        )
        self.component_tree_view.setItemDelegate(self.component_delegate)
        self.component_tree_view.setModel(self.component_model)

    def show_edit_component_dialog(self):
        selected_component = self.component_tree_view.selectedIndexes()[
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
            self.instrument.nexus.load_file(
                map_of_entries[combo.currentText()], nexus_file
            )
            self._set_up_component_model()
            self._update_views()

        # Connect the clicked signal of the ok_button to instrument.load_file and pass the file and entry group object.
        ok_button.clicked.connect(_load_current_entry)

        self.entries_dialog.setLayout(QGridLayout())

        self.entries_dialog.layout().addWidget(QLabel("Entry:"))
        self.entries_dialog.layout().addWidget(combo)
        self.entries_dialog.layout().addWidget(ok_button)
        self.entries_dialog.show()

    def _set_button_state(self):
        set_button_states(
            self.component_tree_view,
            self.delete_action,
            self.duplicate_action,
            self.new_rotation_action,
            self.new_translation_action,
            self.create_link_action,
            self.zoom_action,
            self.edit_component_action,
        )

    def on_create_link(self):
        selected = self.component_tree_view.selectedIndexes()
        if len(selected) > 0:
            self.component_model.add_link(selected[0])
            self._expand_transformation_list(selected[0])
            self._set_button_state()

    def on_duplicate_node(self):
        selected = self.component_tree_view.selectedIndexes()
        if len(selected) > 0:
            self.component_model.duplicate_node(selected[0])
            self._expand_transformation_list(selected[0])

    def _expand_transformation_list(self, node: QModelIndex):
        expand_transformation_list(node, self.component_tree_view, self.component_model)

    def _add_transformation(self, transformation_type: TransformationType):
        add_transformation(
            transformation_type, self.component_tree_view, self.component_model
        )

    def set_up_warning_window(self):
        """
        Sets up the warning dialog that is shown when the definitions submodule has not been cloned.
        :return:
        """

        # Will contain .git even if missing so check that it does not contain just that file.
        if (
            not os.path.exists(self.definitions_dir)
            or len(os.listdir(self.definitions_dir)) <= 1
        ):
            show_warning_dialog(
                "Warning: NeXus definitions are missing. Did you forget to clone the submodules?\n run git submodule update --init ",
                title="NeXus definitions missing",
                parent=self,
            )

    def update_nexus_file_structure_view(self, nexus_file):
        self.treemodel.clear()
        self.treemodel.insertH5pyObject(nexus_file)

    def save_to_nexus_file(self):
        filename = file_dialog(True, "Save Nexus File", NEXUS_FILE_TYPES)
        self.instrument.nexus.save_file(filename)

    def save_to_filewriter_json(self):
        filename = file_dialog(True, "Save Filewriter JSON File", JSON_FILE_TYPES)
        if filename:
            dialog = FilewriterCommandDialog()
            dialog.exec_()
            nexus_file_name, broker, start_time, stop_time, service_id, abort_on_uninitialised_stream, use_swmr = (
                dialog.get_arguments()
            )
            with open(filename, "w") as file:
                filewriter_json_writer.generate_json(
                    self.instrument,
                    file,
                    nexus_file_name=nexus_file_name,
                    broker=broker,
                    start_time=start_time,
                    stop_time=stop_time,
                    service_id=service_id,
                    abort_uninitialised=abort_on_uninitialised_stream,
                    use_swmr=use_swmr,
                )

    def save_to_forwarder_json(self):
        filename = file_dialog(True, "Save Forwarder JSON File", JSON_FILE_TYPES)
        if filename:
            provider_type, ok_pressed = QInputDialog.getItem(
                None,
                "Provider type",
                "Select provider type for PVs",
                ["ca", "pva"],
                0,
                False,
            )
            if ok_pressed:
                with open(filename, "w") as file:
                    nexus_constructor.json.forwarder_json_writer.generate_forwarder_command(
                        file, self.instrument.nexus.entry, provider_type=provider_type
                    )

    def open_nexus_file(self):
        filename = file_dialog(False, "Open Nexus File", NEXUS_FILE_TYPES)
        existing_file = self.instrument.nexus.nexus_file
        if self.instrument.nexus.open_file(filename):
            self._update_views()
            existing_file.close()

    def open_json_file(self):
        filename = file_dialog(False, "Open File Writer JSON File", JSON_FILE_TYPES)
        if filename:
            with open(filename, "r") as json_file:
                json_data = json_file.read()

                try:
                    nexus_file = json_to_nexus(json_data)
                except Exception as exception:
                    show_warning_dialog(
                        "Provided file not recognised as valid JSON",
                        "Invalid JSON",
                        f"{exception}",
                        parent=self,
                    )
                    return

                existing_file = self.instrument.nexus.nexus_file
                if self.instrument.nexus.load_nexus_file(nexus_file):
                    self._update_views()
                    existing_file.close()

    def _update_transformations_3d_view(self):
        self.sceneWidget.clear_all_transformations()
        for component in self.instrument.get_component_list():
            if component.name != "sample":
                self.sceneWidget.add_transformation(component.name, component.transform)

    def _update_views(self):
        self.sceneWidget.clear_all_transformations()
        self.sceneWidget.clear_all_components()
        self._update_3d_view_with_component_shapes()
        self._set_up_component_model()

    def _update_3d_view_with_component_shapes(self):
        for component in self.instrument.get_component_list():
            shape, positions = component.shape
            self.sceneWidget.add_component(component.name, shape, positions)
            self.sceneWidget.add_transformation(component.name, component.transform)

    def show_add_component_window(self, component: Component = None):
        self.add_component_window = QDialog()
        self.add_component_window.ui = AddComponentDialog(
            self.instrument,
            self.component_model,
            component,
            definitions_dir=self.definitions_dir,
            parent=self,
        )
        self.add_component_window.ui.setupUi(self.add_component_window)
        self.add_component_window.show()

    def on_delete_item(self):
        selected = self.component_tree_view.selectedIndexes()
        for item in selected:
            self.component_model.remove_node(item)
        self._set_button_state()

    def on_zoom_item(self):
        selected = self.component_tree_view.selectedIndexes()[0]
        component = selected.internalPointer()
        self.sceneWidget.zoom_to_component(
            self.sceneWidget.get_entity(component.name), self.sceneWidget.view.camera()
        )
