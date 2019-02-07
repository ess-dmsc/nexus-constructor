import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Scene3D 2.0
import QtQuick.Dialogs 1.3
import MyJson 1.0
import MyModels 1.0
import MyWriters 1.0
import "."

ApplicationWindow {

    title: "Nexus Constructor"
    id: window
    visible: true
    width: 1100
    height: 500
    minimumWidth: windowPane.implicitWidth
    minimumHeight: menuBar.implicitHeight + windowPane.implicitHeight

    property string jsonMode: "liveFW"

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
                text: "Export to FileWriter"
                onTriggered: nexusSaveDialog.open()
            }
            Action {
                text: "Export to NeXus file"
                onTriggered: nexusFileDialog.open()
            }
            Action {
                text: "Write to console"
                onTriggered: hdfWriter.print_instrument_to_console(components)
            }
        }
        Menu {
            title: "JSON"
            RadioButton {
                text: "Show Nexus FileWriter JSON"
                checked: true
                onClicked: {
                    jsonMode = "liveFW"
                    jsonConnector.request_filewriter_json(components)
                }
            }
            RadioButton {
                text: "Show Nexus Constructor JSON"
                onClicked: {
                    jsonMode = "liveGC"
                    jsonConnector.request_nexus_constructor_json(components)
                }
            }
            RadioButton {
                text: "Hide JSON display"
                onClicked: jsonMode = "hidden"
            }
        }
    }

    function positionChildWindow(child) {
        // position child window in the center of the main window
        var centralX = window.x + ((window.width - child.width) / 2)
        var centralY = window.y + ((window.height - child.height) / 2)
        // if that's offscreen, position its upper left corner in center of the screen
        var screenX = centralX - window.screen.virtualX
        var screenY = centralY - window.screen.virtualY
        if (screenX > window.screen.width || screenY > window.screen.height || screenX < 0 || screenY < 0){
            centralX = window.screen.width / 2
            centralY = window.screen.height / 2
        }

        child.x = centralX
        child.y = centralY
    }

    Pane {
        id: windowPane
        padding: 5
        focus: true
        anchors.fill: parent
        contentWidth: componentFieldsArea.implicitWidth + instrumentViewArea.implicitWidth + jsonPane.implicitWidth
        contentHeight: Math.max(componentFieldsArea.implicitHeight, instrumentViewArea.implicitHeight, jsonPane.implicitHeight)

        ComponentControls {
            id: componentFieldsArea
            anchors.top: parent.top
            anchors.bottom: statusPane.top
            anchors.left: parent.left
            leftPadding: 0
        }

        Frame {
            id: instrumentViewArea
            anchors.top: parent.top
            anchors.bottom: statusPane.top
            anchors.left: componentFieldsArea.right
            anchors.right: jsonPane.left
            contentWidth: 100
            contentHeight: 100
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
            anchors.bottom: statusPane.top
            anchors.right: parent.right
            contentWidth: 300

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

            states: State {
                name: "hidden"; when: jsonMode == "hidden"
                PropertyChanges { target: jsonPane; visible: false }
                PropertyChanges { target: jsonPane; width: 0 }
            }
        }

        Pane {
            id: statusPane
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.left: parent.left
            height: 20
            Text {
                text: "Running..."
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                visible: LongRunningTask.running

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

    JsonConnector {
        id: jsonConnector
        Component.onCompleted: {
            // When requested json is produced, update the json model with it
            jsonConnector.requested_nexus_constructor_json.connect(jsonModel.set_json)
            jsonConnector.requested_filewriter_json.connect(jsonModel.set_json)
            // Request initial json
            request_filewriter_json(components)
        }
    }
    // When the model updates, request new json for the view if desired
    Connections {
        target: components
        onModel_updated: {
            LongRunningTask.running = true
            jsonConnector.request_filewriter_json(components)
            LongRunningTask.running = false
        }
        enabled: jsonMode == "liveFW"
    }
    Connections {
        target: components
        onModel_updated: {
            LongRunningTask.running = true
            jsonConnector.request_nexus_constructor_json(components)
            LongRunningTask.running = false
        }
        enabled: jsonMode == "liveGC"
    }

    FileDialog {
        id: nexusFileDialog
        title: "Choose a file to write to"
        nameFilters: ["Nexus files (*.nxs *.nx5)", "HDF5 files (*.hdf5)"]
        defaultSuffix: "nxs"
        selectExisting: false
        onAccepted: {
            LongRunningTask.running = true
            hdfWriter.save_instrument(fileUrl, components)
            LongRunningTask.running = false
        }
    }

    FileDialog {
        id: jsonSaveDialog
        title: "Choose file to save to"
        nameFilters: ["JSON file (*.json)"]
        defaultSuffix: "json"
        selectExisting: false
        onAccepted: {
            LongRunningTask.running = true
            jsonConnector.save_to_nexus_constructor_json(fileUrl, components)
            LongRunningTask.running = false
        }
    }

    FileDialog {
        id: jsonLoadDialog
        title: "Choose file to load from"
        nameFilters: ["JSON (*.json)", "All files (*)"]
        onAccepted: {
            LongRunningTask.running = true
            jsonConnector.load_file_into_instrument_model(fileUrl, components)
            LongRunningTask.running = false
        }
    }

    FileDialog {
        id: nexusSaveDialog
        title: "Save FileWriter json to"
        nameFilters: ["JSON file (*.json)"]
        defaultSuffix: "json"
        selectExisting: false
        onAccepted: {
            LongRunningTask.running = true
            jsonConnector.save_to_filewriter_json(fileUrl, components)
            LongRunningTask.running = false
        }
    }
}