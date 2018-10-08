import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Scene3D 2.0
import Qt.labs.platform 1.0 as Labs
import MyModels 1.0
import MyWriters 1.0

ApplicationWindow {

    title: "Nexus Geometry Constructor"
    id: window
    objectName: "window"
    visible: true
    width: 700
    height: 300

    menuBar: MenuBar {
        Menu {
            title: "File"
            Action {
                text: "Open"
                enabled: false
                onTriggered: myLogger.log("Hello World!")
            }
            Action {
                text: "Save"
                enabled: false
                onTriggered: myLogger.log("Hello World!")
            }
            Action {
                text: "Save As"
                enabled: false
                onTriggered: myLogger.log("Hello World!")
            }
            Action {
                text: "Write to console"
                onTriggered: hdfWriter.write_instrument("foo.txt", components)
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

            width: 365;
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

                AnimatedEntity {}
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
        objectName: "components"
    }

    Logger {
        id: myLogger
    }

    HdfWriter {
        id: hdfWriter
    }

    Labs.FileDialog {
        id: fileDialog
        title: "Choose a file to write to"
        fileMode: Labs.FileDialog.SaveFile
        onAccepted: {
            var path = fileDialog.file.toString()
            // h5py requires a path, remove the file protocol if present
            var prefix = "file:///"
            if (path.startsWith(prefix)){
                path = path.substring(prefix.length)
            }
            hdfWriter.write_instrument(path, components)
        }
    }
}
