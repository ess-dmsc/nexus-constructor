import QtQuick 2.11
import QtQuick.Controls 2.4
import Qt.labs.platform 1.0
import MyWriters 1.0
import MyModels 1.0

Rectangle {

    Row {
        id: textRow

        Text {
            id: nameLabel
            text: "Name:"
        }
        TextField {
            id: nameField
            text: "Valjean"
        }
    }

    Row {
        id: facesRow
        anchors.top: textRow.bottom

        Text {
            id: facesLabel
            text: "Faces:"
        }
        TextField {
            id: facesField
            text: "2, 4, 6, 0, 1"
        }
        Button {
            id: addPixel
            text: "Add pixel"
            onClicked: {
                myLogger.log("Adding new pixel")
                pixelListView.model.insert_pixel(nameField.text, facesField.text)
            }
        }
    }

    ListView {
        id: pixelListView
        model: pixelData
        delegate: pixelDelegate
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: facesRow.bottom
        anchors.bottom: writeButtonRow.top
    }

    PixelModel{
        id: pixelData
    }

    Row {
        id: writeButtonRow
        anchors.bottom: parent.bottom

        Button {
            id: writeButton
            text: "Write geometry"
            onClicked: {
                myLogger.log("writing geometry")
                hdfWriter.write_pixels(filenameField.text, pixelData)
                myLogger.log("written")
            }
        }

        TextField {
            id: filenameField
            text: "file.hdf5"
        }

        Button {
            text: "Choose file"
            onClicked: fileDialog.open()
        }
    }

    FileDialog {
        id: fileDialog
        title: "Choose a file to write to"
        onAccepted: {
            var path = fileDialog.file.toString()
            // h5py requires a path, remove the file protocol if present
            var prefix = "file:///"
            if (path.startsWith(prefix)){
                path = path.substring(prefix.length)
            }
            filenameField.text = path
        }
    }

    Logger {
        id: myLogger
    }

    HdfWriter {
        id: hdfWriter
    }

    Component {
        id: pixelDelegate
        Row {
            Text {
                width: 100
                text: "<b>Name:</b>" + name
            }
            Text {
                width: 185
                text: "<b>Faces:</b>" + faces.join(", ")
            }
            Button {
                text: "Remove"
                onClicked: pixelData.remove_pixel(index)
                background: Rectangle {
                    border.color: "#f00"
                    border.width: parent.pressed ? 2 : 1
                    radius: 8
                    // darker button when hovered-over, or tab-selected
                    color: (parent.hovered || parent.activeFocus) ? "#f88" : "#faa"
                }
            }
        }
    }
}