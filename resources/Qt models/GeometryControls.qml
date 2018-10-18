import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Dialogs 1.3
import MyModels 1.0


Pane {
    property var geometryModel

    id: pane
    padding: 0

    ListView {
        id: view
        anchors.fill: parent
        interactive: false
    }

    OFFModel {
        id: offModel
    }

    CylinderModel {
        id: cylinderModel
    }

    Component {
        id: offDelegate
        Item {
            id: offContainer
            width: parent.width
            height: Math.max(fileTextField.height, chooseFileButton.height)

            LabeledTextField {
                id: fileTextField
                anchors.top: parent.top
                anchors.left: parent.left
                labelText: "OFF file:"
                editorText: filename
                editorWidth: 200
                onEditingFinished: filename = editorText
            }
            Button {
                id: chooseFileButton
                anchors.verticalCenter: fileTextField.verticalCenter
                anchors.left: fileTextField.right
                text: "Choose file"
                onClicked: filePicker.open()
            }
            FileDialog {
                id: filePicker
                title: "Choose geometry file"
                nameFilters: ["Object File Format (*.off)", "All files (*)"]
                onAccepted: {
                    filename = filePicker.fileUrl
                    fileTextField.editorText = filePicker.fileUrl
                }
            }
        }
    }

    Component {
        id: cylinderDelegate
        Item {
            id: cylinderContainer
            width: parent.width
            height: cylinderLabel.height + fields.height

            Label {
                id: cylinderLabel
                anchors.top: parent.top
                anchors.left: parent.left
                text: "Cylinder Geometry:"
            }

            Frame {
                id: fields
                anchors.top: cylinderLabel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                contentHeight: heightField.height + directionLabel.height + axisXField.height

                LabeledTextField {
                    id: heightField
                    anchors.top: parent.top
                    anchors.left: parent.left
                    labelText: "height:"
                    editorText: cylinder_height
                    onEditingFinished: cylinder_height = parseFloat(editorText)
                }
                LabeledTextField {
                    id: radiusField
                    anchors.top: heightField.top
                    anchors.left: heightField.right
                    labelText: "radius:"
                    editorText: cylinder_radius
                    onEditingFinished: cylinder_radius = parseFloat(editorText)
                }

                Label {
                    id: directionLabel
                    anchors.top: radiusField.bottom
                    anchors.left: parent.left
                    text: "axis direction:"
                }

                LabeledTextField {
                    id: axisXField
                    anchors.top: directionLabel.bottom
                    anchors.left: parent.left
                    labelText: "x:"
                    editorText: axis_x
                    onEditingFinished: axis_x = parseFloat(editorText)
                }
                LabeledTextField {
                    id: axisYField
                    anchors.top: axisXField.top
                    anchors.horizontalCenter: parent.horizontalCenter
                    labelText: "y:"
                    editorText: axis_y
                    onEditingFinished: axis_y = parseFloat(editorText)
                }
                LabeledTextField {
                    id: axisZField
                    anchors.top: axisXField.top
                    anchors.right: parent.right
                    labelText: "z:"
                    editorText: axis_z
                    onEditingFinished: axis_z = parseFloat(editorText)
                }
            }
        }
    }


    states: [
        State {
            name: "OFF"
            PropertyChanges { target: pane; geometryModel: offModel }

            PropertyChanges { target: view; model: offModel}
            PropertyChanges { target: view; delegate: offDelegate}
        },
        State {
            name: "Cylinder"
            PropertyChanges { target: pane; geometryModel: cylinderModel }

            PropertyChanges { target: view; model: cylinderModel}
            PropertyChanges { target: view; delegate: cylinderDelegate}
        }
    ]
}
