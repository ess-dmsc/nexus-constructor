import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Dialogs 1.3
import MyModels 1.0


Pane {
    property string offFile: ""

    property real cylinder_axis_x
    property real cylinder_axis_y
    property real cylinder_axis_z
    property real cylinder_height
    property real cylinder_radius

    property var geometryModel

    id: pane
    padding: 2

    Item {
        id: offContainer
        width: parent.width
        height: Math.max(fileTextField.height, chooseFileButton.height)
        visible: false

        LabeledTextField {
            id: fileTextField
            anchors.top: parent.top
            anchors.left: parent.left
            labelText: "OFF file:"
            editorWidth: 200
            onEditingFinished: offFile = editorText
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
            nameFilters: ["Object File Format (*.off)"]
            onAccepted: fileTextField.editorText = filePicker.fileUrl
        }
        OFFModel {
            id: offModel

        }
    }

    Item {
        id: cylinderContainer
        width: parent.width
        height: cylinderLabel.height + heightField.height +
                directionLabel.height + axisXField.height
        visible: false

        Label {
            id: cylinderLabel
            anchors.top: parent.top
            anchors.left: parent.left
            text: "Cylinder:"
        }

        LabeledTextField {
            id: heightField
            anchors.top: cylinderLabel.bottom
            anchors.left: parent.left
            labelText: "height:"
            onEditingFinished: cylinder_height = parseFloat(editorText)
        }
        LabeledTextField {
            id: radiusField
            anchors.top: heightField.top
            anchors.left: heightField.right
            labelText: "radius:"
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
            onEditingFinished: cylinder_axis_x = parseFloat(editorText)
        }
        LabeledTextField {
            id: axisYField
            anchors.top: axisXField.top
            anchors.horizontalCenter: parent.horizontalCenter
            labelText: "y:"
            onEditingFinished: cylinder_axis_y = parseFloat(editorText)
        }
        LabeledTextField {
            id: axisZField
            anchors.top: axisXField.top
            anchors.right: parent.right
            labelText: "z:"
            onEditingFinished: cylinder_axis_z = parseFloat(editorText)
        }
        CylinderModel {
            id: cylinderModel
        }
    }


    states: [
        State {
            name: "OFF"
            PropertyChanges { target: offContainer; visible: true }
            PropertyChanges { target: pane; contentHeight: offContainer.height }
            PropertyChanges { target: pane; geometryModel: offModel }
        },
        State {
            name: "Cylinder"
            PropertyChanges { target: cylinderContainer; visible: true }
            PropertyChanges { target: pane; contentHeight: cylinderContainer.height }
            PropertyChanges { target: pane; geometryModel: cylinderModel }
        }
    ]
}
