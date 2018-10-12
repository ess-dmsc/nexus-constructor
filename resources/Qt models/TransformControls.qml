import QtQuick 2.11
import QtQuick.Controls 2.4

/*
 * Controls for defining a components transformation to detector space.
 * Should be used as part of a delegate in a view on an InstrumentModel.
 * That instrumentModel should be available from the containing qml file
 * with the id 'components' so that it can be read to select a
 * transformation parent.
 */

Item {
    height: nameField.height +
            relativePicker.height +
            rotateLabel.height +
            xRotField.height +
            angleField.height +
            translateLabel.height +
            xField.height
    width: parent.width

    LabeledTextField {
        id: nameField
        labelText: "Name:"
        editorText: name
        onEditingFinished: name = editorText
    }

    Label {
        id: relativeLabel
        anchors.verticalCenter: relativePicker.verticalCenter
        anchors.left: parent.left
        text: "Transform relative to:"
    }
    ComboBox {
        id: relativePicker
        anchors.top: nameField.bottom
        anchors.left: relativeLabel.right
        model: components
        textRole: "name"
        currentIndex: transform_parent_index
        onCurrentIndexChanged: transform_parent_index = currentIndex
    }

    Label {
        id: rotateLabel
        anchors.top: relativePicker.bottom
        anchors.left: parent.left
        text: "Rotate"
    }

    LabeledTextField {
        id: xRotField
        anchors.top: rotateLabel.bottom
        anchors.left: parent.left
        labelText: "x:"
        editorText: rotate_x
        onEditingFinished: rotate_x = parseFloat(editorText)
    }
    LabeledTextField {
        id: yRotField
        anchors.top: xRotField.top
        anchors.left: xRotField.right
        labelText: "y:"
        editorText: rotate_y
        onEditingFinished: rotate_y = parseFloat(editorText)
    }
    LabeledTextField {
        id: zRotField
        anchors.top: xRotField.top
        anchors.left: yRotField.right
        labelText: "z:"
        editorText: rotate_z
        onEditingFinished: rotate_z = parseFloat(editorText)
    }

    LabeledTextField {
        id: angleField
        anchors.top: xRotField.bottom
        anchors.right: zRotField.right
        labelText: "angle (degrees):"
        editorText: rotate_angle
        onEditingFinished: rotate_angle = parseFloat(editorText)
    }

    Label {
        id: translateLabel
        anchors.top: angleField.bottom
        anchors.left: parent.left
        text: "Translate"
    }

    LabeledTextField {
        id: xField
        anchors.top: translateLabel.bottom
        anchors.left: parent.left
        labelText: "x:"
        editorText: translate_x
        onEditingFinished: translate_x = parseFloat(editorText)
    }
    LabeledTextField {
        id: yField
        anchors.top: xField.top
        anchors.left: xField.right
        labelText: "y:"
        editorText: translate_y
        onEditingFinished: translate_y = parseFloat(editorText)
    }
    LabeledTextField {
        id: zField
        anchors.top: xField.top
        anchors.left: yField.right
        labelText: "z:"
        editorText: translate_z
        onEditingFinished: translate_z = parseFloat(editorText)
    }
}
