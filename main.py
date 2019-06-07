"""
Entry script for the nexus constructor application.
Requires Python 3.6+
"""

import sys
import h5py
from PySide2.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog
from PySide2 import QtCore
from ui.mainwindow import Ui_MainWindow
import silx.gui.hdf5

from nexus_constructor.qml_models import instrument_model
from nexus_constructor.nexus_filewriter_json import writer

NEXUS_FILE_TYPES = "NeXus Files (*.nxs,*.nex,*.nx5)"


def set_up_in_memory_nexus_file():
    return h5py.File("nexus-constructor", mode="x", driver="core", backing_store=False)


class MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.nexus_file = set_up_in_memory_nexus_file()
        self.entry_group = self.nexus_file.create_group("entry")
        self.entry_group.attrs["NX_class"] = "NXentry"
        self.instrument_group = self.entry_group.create_group("instrument")
        self.instrument_group.attrs["NX_class"] = "NXinstrument"

        self.components_list_model = instrument_model.InstrumentModel()
        self.components_list_model.initialise(self.entry_group)

    file_dialog_native = QFileDialog.DontUseNativeDialog

    def setupUi(self, main_window):
        super().setupUi(main_window)

        self.addWindow = QDialog()

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
        self.treemodel.insertH5pyObject(self.nexus_file)
        self.treemodel.setDatasetDragEnabled(True)
        self.treemodel.setFileDropEnabled(True)
        self.treemodel.setFileMoveEnabled(True)
        self.verticalLayout.addWidget(self.widget)
        self.listView.setModel(self.components_list_model)

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
            with open(fileName, "w") as file:
                file.write(writer.generate_json(self.components_list_model))

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
            self.widget.findHdf5TreeModel().clear()
            self.widget.findHdf5TreeModel().insertH5pyObject(self.nexus_file)
            print("NeXus file loaded")

    def show_add_component_window(self):
        self.addWindow.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    window = QMainWindow()
    ui = MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
