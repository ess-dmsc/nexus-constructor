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

    function saveFields(){
        name = nameField.editorText
        transform_parent_index = relativePicker.currentIndex
        rotate_x = parseFloat(xRotField.editorText)
        rotate_y = parseFloat(yRotField.editorText)
        rotate_z = parseFloat(zRotField.editorText)
        rotate_angle = parseFloat(angleField.editorText)
        translate_x = parseFloat(xField.editorText)
        translate_y = parseFloat(yField.editorText)
        translate_z = parseFloat(zField.editorText)
    }

    LabeledTextField {
        id: nameField
        labelText: "Name:"
        editorText: name
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
    }
    LabeledTextField {
        id: yRotField
        anchors.top: xRotField.top
        anchors.left: xRotField.right
        labelText: "y:"
        editorText: rotate_y
    }
    LabeledTextField {
        id: zRotField
        anchors.top: xRotField.top
        anchors.left: yRotField.right
        labelText: "z:"
        editorText: rotate_z
    }

    LabeledTextField {
        id: angleField
        anchors.top: xRotField.bottom
        anchors.right: zRotField.right
        labelText: "angle (degrees):"
        editorText: rotate_angle
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
    }
    LabeledTextField {
        id: yField
        anchors.top: xField.top
        anchors.left: xField.right
        labelText: "y:"
        editorText: translate_y
    }
    LabeledTextField {
        id: zField
        anchors.top: xField.top
        anchors.left: yField.right
        labelText: "z:"
        editorText: translate_z
    }
}
