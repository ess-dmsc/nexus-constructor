import QtQuick 2.11
import QtQuick.Controls 2.4
import Qt.labs.platform 1.0
import MyWriters 1.0
import MyModels 1.0

Pane {

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
            objectName: "addPixel"
            text: "Add pixel"
            onClicked: {
                myLogger.log("Adding new pixel")
                pixelData.add_pixel(nameField.text, facesField.text)
            }
        }
    }

    Frame {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: facesRow.bottom
        anchors.bottom: writeButtonRow.top
        padding: 1
        ListView {
            id: pixelListView
            objectName: "pixelListView"
            model: pixelData
            delegate: pixelDelegate
            anchors.fill: parent
            clip: true
        }
    }

    PixelModel{
        id: pixelData
        objectName: "pixelData"
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
        Frame {
            id: pixelBox
            padding: 5
            contentHeight: mainContent.height + extendedContent.height
            width: pixelListView.width

            MouseArea {
                anchors.fill: parent
                onClicked: pixelBox.state = (pixelBox.state == "Extended") ? "" : "Extended"
            }

            Item {
                id: mainContent
                anchors.left: parent.left
                anchors.right: parent.right
                height: removeButton.height
                Text {
                    id: nameLabel
                    anchors.left: parent.left
                    anchors.top: parent.top
                    width: 100
                    text: "<b>Name:</b>" + name
                }
                Text {
                    id: faceLabel
                    anchors.left: nameLabel.right
                    anchors.right: removeButton.left
                    anchors.top: parent.top
                    width: 185
                    text: "<b>Faces:</b>" + faces.join(", ")
                }
                Button {
                    id: removeButton
                    anchors.right: expansionCaret.left
                    anchors.rightMargin: 5
                    anchors.top: parent.top
                    text: "Remove"
                    objectName: "removePixelButton"
                    onClicked: pixelData.remove_pixel(index)
                    background: Rectangle {
                        border.color: "#f00"
                        border.width: parent.pressed ? 2 : 1
                        radius: 8
                        // darker button when hovered-over, or tab-selected
                        color: (parent.hovered || parent.activeFocus) ? "#f88" : "#faa"
                    }
                }
                Image {
                    id: expansionCaret
                    width: 20; height: 20;
                    anchors.right: parent.right
                    anchors.top: parent.top
                    source: "file:resources/images/caret.svg"
                    transformOrigin: Item.Center
                    rotation: 0
                }
            }

            Item {
                id: extendedContent
                anchors.top: mainContent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 0
                visible: false
                Text{
                    id: extendedText
                    text: "I have been extended"
                }
            }

            states: State {
                name: "Extended"

                PropertyChanges { target: extendedContent; height: extendedText.height }
                PropertyChanges { target: extendedContent; visible: true }
                PropertyChanges { target: expansionCaret; rotation: 180 }
            }
        }
    }
}
