"""
Entry script for the nexus constructor application.
Requires Python 3.5+
"""

import sys
from os import path, environ
from uuid import uuid4

import h5py
from PySide2 import QtCore
import sys
import h5py
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog
from PySide2 import QtCore
from ui.mainwindow import Ui_MainWindow
from ui.componentdetails import Ui_ComponentDetailsDialog
from ui.addcomponentwindow import Ui_AddComponentDialog
from uuid import uuid4
from component_names import component_names
import silx.gui.hdf5

from nexus_constructor.application import Application
from PySide2.QtGui import QGuiApplication, QIcon
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog

NEXUS_FILE_TYPES = "NeXus Files (*.nxs,*.nex,*.nx5)"


def set_up_in_memory_nexus_file():
    return h5py.File(str(uuid4()), mode="w", driver="core", backing_store=False)

class MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.nexus_file = set_up_in_memory_nexus_file()
        self.entry_group = self.nexus_file.create_group("entry")
        self.entry_group.attrs["NX_class"] = "NXentry"
        self.instrument_group = self.entry_group.create_group("/instrument")
        self.instrument_group.attrs["NX_class"] = "NXinstrument"

    file_dialog_native = QFileDialog.DontUseNativeDialog

    def setupUi(self, main_window):
        super().setupUi(main_window)

        self.addWindow = QDialog()
        self.addWindow.ui = AddComponentDialog(self.entry_group)
        self.addWindow.ui.setupUi(self.addWindow)

        self.pushButton.clicked.connect(self.show_add_component_window)
        self.actionExport_to_NeXus_file.triggered.connect(self.save_to_nexus_file)
        self.actionOpen_NeXus_file.triggered.connect(self.open_nexus_file)
        self.actionExport_to_Filewriter_JSON.triggered.connect(
            self.save_to_filewriter_json
        )

        self.widget = silx.gui.hdf5.Hdf5TreeView()
        self.widget.findHdf5TreeModel().insertH5pyObject(self.nexus_file)
        self.verticalLayout.addWidget(self.widget)

        self.widget.setVisible(True)

    def save_to_nexus_file(self):
        options = QFileDialog.Options()
        options |= self.file_dialog_native
        fileName, _ = QFileDialog.getSaveFileName(
            parent=None,
            caption="QFileDialog.getSaveFileName()",
            directory="",
            filter=f"{NEXUS_FILE_TYPES};;All Files (*)",
            options=options,
        )
        if fileName:
            print(fileName)
            file = h5py.File(fileName, mode="x")
            try:
                file.copy(source=self.nexus_file["/entry/"], dest="/entry/")
                print("Saved to NeXus file")
            except ValueError as e:
                print(f"File writing failed: {e}")

    def save_to_filewriter_json(self):
        options = QFileDialog.Options()
        options |= self.file_dialog_native
        fileName, _ = QFileDialog.getSaveFileName(
            parent=None,
            caption="QFileDialog.getSaveFileName()",
            directory="",
            filter="JSON Files (*.json);;All Files (*)",
            options=options,
        )
        if fileName:
            print(fileName)

    def open_nexus_file(self):
        options = QFileDialog.Options()

        options |= self.file_dialog_native
        fileName, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption="QFileDialog.getOpenFileName()",
            directory="",
            filter=f"{NEXUS_FILE_TYPES};;All Files (*)",
            options=options,
        )
        if fileName:
            print(fileName)
            self.nexus_file = h5py.File(
                fileName, mode="r", backing_store=False, driver="core"
            )
            print("NeXus file loaded")

    def show_add_component_window(self):
        self.addWindow.exec()


class ComponentDetailsDialog(Ui_ComponentDetailsDialog):
    def __init__(self, entry_group):
        super().__init__()
        self.component_name = False
        self.component_type = False
        self.geometry_type = False
        self.pixel_type = False
        self.entry_group = entry_group

    def setupUi(self, ComponentDetailsDialog):
        super().setupUi(ComponentDetailsDialog)
        self.buttonBox.rejected.connect(self.set_defaults)
        self.buttonBox.accepted.connect(self.add_component)

    def closeEvent(self, event):
        print("window closed")
        # doesn't seem to be working, no idea why.
        self.set_defaults()

    def create_delegates(self, component_type, geometry_type, pixel_type):
        self.component_type = component_type
        self.geometry_type = geometry_type
        self.pixel_type = pixel_type
        if self.geometry_type == "Cylinder":
            self.GeometryFileBox.setVisible(False)
        if self.geometry_type == "Mesh":
            self.CylinderGeometryBox.setVisible(False)
        else:
            self.CylinderGeometryBox.setVisible(False)
            self.GeometryFileBox.setVisible(False)

    def set_defaults(self):
        self.CylinderGeometryBox.setVisible(True)
        self.GeometryFileBox.setVisible(True)

    def add_component(self):
        component_name = str(self.componentNameField.text())
        group = self.entry_group.create_group(name=component_name)
        group.attrs["NX_class"] = component_names[self.component_type]
        # TODO: close the dialog


class AddComponentDialog(Ui_AddComponentDialog):
    def __init__(self, group):
        super().__init__()
        self.entry_group = group

    def setupUi(self, add_component_window):
        super().setupUi(add_component_window)
        self.buttonBox.accepted.connect(self.accepted)

        self.populate_components_box()
        self.details = QDialog()
        self.details.ui = ComponentDetailsDialog(self.entry_group)
        self.details.ui.setupUi(self.details)

    def populate_components_box(self):
        index = 0
        for component in component_names.items():
            self.ComponentTypeComboBox.insertItem(index, component[0])
            index += 1

    def accepted(self):
        # create the next window here and pass stuff in

        self.details.ui.create_delegates(
            self.ComponentTypeComboBox.currentText(),
            self.GeometryTypeComboBox.currentText(),
            self.PixelTypeComboBox.currentText(),
        )
        self.details.exec()



if __name__ == "__main__":
    location = sys.executable if getattr(sys, "frozen", False) else __file__
    resource_folder = path.join(path.dirname(location), "resources")

    environ["QT_QUICK_CONTROLS_CONF"] = path.join(
        resource_folder, "qtquickcontrols2.conf"
    )

    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setWindowIcon(QIcon(path.join(resource_folder, "images", "icon.png")))

    window = QMainWindow()
    ui = MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
