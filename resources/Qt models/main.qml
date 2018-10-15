import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Scene3D 2.0
import QtQuick.Dialogs 1.3
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
                enabled: false
                onTriggered: myLogger.log("'Open' menu item clicked")
            }
            Action {
                text: "Save"
                enabled: false
                onTriggered: myLogger.log("'Save' menu item clicked")
            }
            Action {
                text: "Save As"
                onTriggered: fileDialog.open()
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
    }

    Logger {
        id: myLogger
    }

    HdfWriter {
        id: hdfWriter
    }

    FileDialog {
        id: fileDialog
        title: "Choose a file to write to"
        nameFilters: ["Nexus files (*.nxs *.nx5)", "HDF5 files (*.hdf5)"]
        defaultSuffix: "nxs"
        selectExisting: false
        onAccepted: hdfWriter.save_instrument(fileDialog.fileUrl, components)
    }
}
