import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Dialogs 1.3
import MyWriters 1.0

Rectangle {
    width: 400; height: 300

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
                var faces = facesField.text.split(",").map(
                    function(s){
                        return {face: parseInt(s.trim())}
                    })
                var pixel = {name: nameField.text, faces: faces}
                pixelListView.model.append(pixel)
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

    function listViewAsJs(){
        var data = []
        for(var i = 0; i < pixelData.count; i++){
            var pixel = pixelData.get(i)
            var faces = []
            for(var j = 0; j < pixel.faces.count; j++){
                faces.push(pixel.faces.get(j).face)
            }
            data.push({
                name: pixel.name,
                faces: faces
            })
        }
        return data
    }

    Row {
        id: writeButtonRow
        anchors.bottom: parent.bottom

        Button {
            id: writeButton
            text: "Write geometry"
            onClicked: {
                myLogger.log("writing geometry")
                var pixels = listViewAsJs()
                myLogger.log_list(pixels)
                hdfWriter.write_pixels(filenameField.text, pixels)
                myLogger.log("written")
            }
        }

        TextField {
            id: filenameField
            text: "file.hdf5"
        }

        Button {
            text: "Choose file"
            onClicked: {
                fileDialog.open()
            }
        }
    }

    FileDialog {
        id: fileDialog
        title: "Choose a file to write to"
        selectExisting: false
        selectFolder: false
        selectMultiple: false
        onAccepted: {
            var path = fileDialog.fileUrl.toString()
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
            Text { text: "<b>Pixel name:</b>" + name + " <b>Faces:</b>" }
            Repeater {
                model: faces
                Text { text: face + "," }
            }
            Button {
                text: "Remove"
                onClicked: {
                    pixelData.remove(index)
                }
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
