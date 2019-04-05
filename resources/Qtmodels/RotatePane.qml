import QtQuick.Controls 1.4
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.11
import MyValidators 1.0

Pane {

    padding: 0
    contentWidth: xRotField.implicitWidth + yRotField.implicitWidth + zRotField.implicitWidth
    contentHeight: rotateNameField.height + xRotField.height + angleField.height

    Label {
        id: rotateLabel
        anchors.verticalCenter: rotateNameField.verticalCenter
        anchors.left: parent.left
        text: "Rotation"
    }
    LabeledTextField {
        id: rotateNameField
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.left: yRotField.left
        anchoredEditor: true
        labelText: "Name:"
        editorText: name
        onEditingFinished: name = editorText
        validator: NameValidator {
            model: transformModel
            myindex: index
            onValidationFailed: translateNameField.ToolTip.show("A component's transforms must have unique names", 3000)
        }
    }

    LabeledTextField {
        id: xRotField
        anchors.top: rotateNameField.bottom
        anchors.left: parent.left
        labelText: "x:"
        editorText: rotate_x
        validator: numberValidator
        onEditingFinished: rotate_x = parseFloat(editorText)
    }
    LabeledTextField {
        id: yRotField
        anchors.top: xRotField.top
        anchors.horizontalCenter: parent.horizontalCenter
        labelText: "y:"
        editorText: rotate_y
        validator: numberValidator
        onEditingFinished: rotate_y = parseFloat(editorText)
    }
    LabeledTextField {
        id: zRotField
        anchors.top: xRotField.top
        anchors.right: parent.right
        labelText: "z:"
        editorText: rotate_z
        validator: numberValidator
        onEditingFinished: rotate_z = parseFloat(editorText)
    }

    LabeledTextField {
        id: angleField
        anchors.top: xRotField.bottom
        anchors.right: zRotField.right
        labelText: "angle (degrees):"
        editorText: rotate_angle
        validator: angleValidator
        onEditingFinished: rotate_angle = parseFloat(editorText)
    }
}