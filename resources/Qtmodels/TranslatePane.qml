import MyValidators 1.0
import QtQuick.Controls 2.5

Pane {

    padding: 0
    contentWidth: xField.implicitWidth + yField.implicitWidth + zField.implicitWidth
    contentHeight: translateNameField.height + xField.height

    Label {
        id: translateLabel
        anchors.verticalCenter: translateNameField.verticalCenter
        anchors.left: parent.left
        text: "Translation"
    }
    LabeledTextField {
        id: translateNameField
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.left: yField.left
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
        id: xField
        anchors.top: translateNameField.bottom
        anchors.left: parent.left
        labelText: "x:"
        editorText: translate_x
        validator: numberValidator
        onEditingFinished: translate_x = parseFloat(editorText)
    }
    LabeledTextField {
        id: yField
        anchors.top: xField.top
        anchors.horizontalCenter: parent.horizontalCenter
        labelText: "y:"
        editorText: translate_y
        validator: numberValidator
        onEditingFinished: translate_y = parseFloat(editorText)
    }
    LabeledTextField {
        id: zField
        anchors.top: xField.top
        anchors.right: parent.right
        labelText: "z:"
        editorText: translate_z
        validator: numberValidator
        onEditingFinished: translate_z = parseFloat(editorText)
    }
}