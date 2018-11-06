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
    width: 1100
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
                text: "Export to nexus file"
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
            anchors.right: jsonPane.left
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

        Pane {
            id: jsonPane
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            width: 300

            ListView {
                id: jsonListView
                model: jsonModel
                delegate: jsonLineDelegate
                anchors.fill: parent
                clip: true

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AlwaysOn
                }
            }

            Component {
                id: jsonLineDelegate
                Label {
                    text: (collapsed ? collapsed_text : full_text)
                    wrapMode: Text.Wrap
                    width: parent.width
                    MouseArea {
                        anchors.fill: parent
                        onClicked: collapsed = !collapsed
                    }
                }
            }
        }
    }

    InstrumentModel{
        id: components
    }

    FilteredJsonModel {
        id: jsonModel
    }

    Logger {
        id: myLogger
    }

    HdfWriter {
        id: hdfWriter
    }

    JsonWriter {
        id: jsonWriter
        Component.onCompleted: {
            // When the model updates, request new json
            components.model_updated.connect(jsonWriter.request_model_json)
            // When requested json is produced, update the model with it
            jsonWriter.requested_model_json.connect(jsonModel.set_json)
            // Request initial json
            jsonWriter.request_model_json(components)
        }
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
