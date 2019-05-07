import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Scene3D 2.0
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.11
import MyJson 1.0
import MyModels 1.0
import MyWriters 1.0

ApplicationWindow {

    title: "Nexus Constructor"
    id: window
    visible: true
    width: 1100
    height: 500
    minimumWidth: centralRow.implicitWidth
    minimumHeight: centralRow.implicitHeight + menuBar.implicitHeight
    property var jsonPaneWidth: 300

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
                    makeRoomForReturnOfJSONPane()
                    jsonMode = "liveFW"
                    jsonConnector.request_filewriter_json(components)
                }
            }
            RadioButton {
                text: "Show Nexus Constructor JSON"
                onClicked: {
                    makeRoomForReturnOfJSONPane()
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

    function makeRoomForReturnOfJSONPane() {
        // Force the window to expand if the JSON pane was hidden and has been made visible again
        if (jsonMode == "hidden" && window.width <= window.minimumWidth)
                window.width += jsonPaneWidth
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

        RowLayout {
            id: centralRow
            anchors.fill: parent
            Layout.minimumWidth: 100

            ComponentControls {
                id: componentFieldsArea
                leftPadding: 0
                Layout.fillHeight: true
                Layout.fillWidth: false
            }

            Frame {
                id: instrumentViewArea
                contentWidth: 300
                contentHeight: 100
                Layout.fillHeight: true
                Layout.fillWidth: true
                focus: true
                padding: 1

                Scene3D {
                    id: scene3d
                    anchors.fill: parent
                    focus: true
                    aspects: ["input", "logic"]
                    cameraAspectRatioMode: Scene3D.AutomaticAspectRatio

                    AnimatedEntity {
                        id: instrumentEntity
                        instrument: components
                    }
                }

                AxisIndicator {
                    id: axisIndicator
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    width: 100
                    height: 100

                    targetCamera: instrumentEntity.camera
                }

                MouseArea {
                    anchors.fill: scene3d
                    onClicked: instrumentViewArea.focus = true
                    enabled: !instrumentViewArea.focus
                }
            }

            JSONPane {
                id: jsonPane
                contentWidth: jsonPaneWidth
                Layout.fillHeight: true
                Layout.fillWidth: false
            }
        }
    }

    NexusModel {
        id: nxsModel
    }

    InstrumentModel{
        id: components
        Component.onCompleted: {
            initialise(nxsModel.entryGroup)
        }
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
            jsonConnector.request_filewriter_json(components)
            instrumentEntity.camera.viewAll()
        }
        enabled: jsonMode == "liveFW"
    }

    Connections {
        target: components
        onModel_updated: jsonConnector.request_nexus_constructor_json(components)
        enabled: jsonMode == "liveGC"
    }

    MessageDialog {
        id: jsonParseErrorMessage
        title: "Error"
        text: "Couldn't parse JSON file."
        onAccepted: {
            jsonParseErrorMessage.close()
        }
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
        onAccepted: jsonConnector.save_to_nexus_constructor_json(fileUrl, components)
    }

    FileDialog {

        id: jsonLoadDialog
        title: "Choose file to load from"
        nameFilters: ["JSON (*.json)", "All files (*)"]
        property var loadSuccessful: true
        onAccepted: {

            loadSuccessful = jsonConnector.load_file_into_instrument_model(fileUrl, components)

            // Display a message if loading the file failed
            if (!loadSuccessful) {
                jsonParseErrorMessage.open()
            }

        }
    }

    FileDialog {
        id: nexusSaveDialog
        title: "Save FileWriter json to"
        nameFilters: ["JSON file (*.json)"]
        defaultSuffix: "json"
        selectExisting: false
        onAccepted: jsonConnector.save_to_filewriter_json(fileUrl, components)
    }
}
