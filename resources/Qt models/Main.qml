import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Scene3D 2.0
import QtQuick.Dialogs 1.3
import MyJson 1.0
import MyModels 1.0
import MyWriters 1.0

ApplicationWindow {

    title: "Nexus Geometry Constructor"
    id: window
    visible: true
    width: 800
    height: 500

    menuBar: MenuBar {
        Menu {
            title: "File"
            Action {
                text: "Open"
                onTriggered: jsonLoadDialog.open()
            }
            Action {
                text: "Save"
                onTriggered: jsonSaveDialog.open()
            }
            Action {
                text: "Save As"
                onTriggered: nexusFileDialog.open()
            }
            Action {
                text: "Write to console"
                onTriggered: hdfWriter.print_instrument_to_console(components)
            }
        }
    }

    Pane {
        padding: 5
        focus: true
        anchors.fill: parent

        ComponentControls {
            id: componentFieldsArea
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            leftPadding: 0

            width: 400;
        }

        Frame {
            id: instrumentViewArea
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: componentFieldsArea.right
            anchors.right: parent.right
            contentWidth: scene3d.implicitWidth
            contentHeight: scene3d.implicitHeight
            focus: true
            padding: 1

            Scene3D {
                id: scene3d
                anchors.fill: parent
                focus: true
                aspects: ["input", "logic"]
                cameraAspectRatioMode: Scene3D.AutomaticAspectRatio

                AnimatedEntity {
                    instrument: components
                }
            }

            MouseArea {
                anchors.fill: scene3d
                onClicked: instrumentViewArea.focus = true
                enabled: !instrumentViewArea.focus
            }
        }
    }

    InstrumentModel{
        id: components
    }

    Logger {
        id: myLogger
    }

    HdfWriter {
        id: hdfWriter
    }

    JsonWriter {
        id: jsonWriter
    }

    JsonLoader {
        id: jsonLoader
    }

    FileDialog {
        id: nexusFileDialog
        title: "Choose a file to write to"
        nameFilters: ["Nexus files (*.nxs *.nx5)", "HDF5 files (*.hdf5)"]
        defaultSuffix: "nxs"
        selectExisting: false
        onAccepted: hdfWriter.save_instrument(fileUrl, components)
    }

    FileDialog {
        id: jsonSaveDialog
        title: "Choose file to save to"
        nameFilters: ["JSON file (*.json)"]
        defaultSuffix: "json"
        selectExisting: false
        onAccepted: jsonWriter.save_json(fileUrl, components)
    }

    FileDialog {
        id: jsonLoadDialog
        title: "Choose file to load from"
        nameFilters: ["JSON (*.json)", "All files (*)"]
        onAccepted: jsonLoader.load_file_into_instrument_model(fileUrl, components)
    }
}
