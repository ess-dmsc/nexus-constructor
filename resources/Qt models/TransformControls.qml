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
            translateLabel.height +
            xField.height +
            rotateLabel.height +
            xRotField.height +
            angleField.height
    width: parent.width

    Label {
        id: nameLabel
        anchors.top: nameField.top
        anchors.left: parent.left
        text: "Name:"
    }
    TextField {
        id: nameField
        anchors.top: parent.top
        anchors.left: nameLabel.right
        text: name
        onEditingFinished: name = text
    }

    Label {
        id: relativeLabel
        anchors.top: relativePicker.top
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
        id: translateLabel
        anchors.top: relativePicker.bottom
        anchors.left: parent.left
        text: "Translate"
    }

    Label {
        id: xLabel
        anchors.top: xField.top
        anchors.left: parent.left
        text: "x:"
    }
    TextField {
        id: xField
        anchors.top: translateLabel.bottom
        anchors.left: xLabel.right
        width: 100
        text: translate_x
        onEditingFinished: translate_x = parseFloat(text)
    }
    Label {
        id: yLabel
        anchors.top: xField.top
        anchors.left: xField.right
        text: "y:"
    }
    TextField {
        id: yField
        anchors.top: xField.top
        anchors.left: yLabel.right
        width: 100
        text: translate_y
        onEditingFinished: translate_y = parseFloat(text)
    }
    Label {
        id: zLabel
        anchors.top: xField.top
        anchors.left: yField.right
        text: "z:"
    }
    TextField {
        id: zField
        anchors.top: xField.top
        anchors.left: zLabel.right
        width: 100
        text: translate_z
        onEditingFinished: translate_z = parseFloat(text)
    }

    Label {
        id: rotateLabel
        anchors.top: xField.bottom
        anchors.left: parent.left
        text: "Rotate"
    }

    Label {
        id: xRotLabel
        anchors.top: xRotField.top
        anchors.left: parent.left
        text: "x:"
    }
    TextField {
        id: xRotField
        anchors.top: rotateLabel.bottom
        anchors.left: xRotLabel.right
        width: 100
        text: rotate_x
        onEditingFinished: rotate_x = parseFloat(text)
    }
    Label {
        id: yRotLabel
        anchors.top: xRotField.top
        anchors.left: xRotField.right
        text: "y:"
    }
    TextField {
        id: yRotField
        anchors.top: xRotField.top
        anchors.left: yRotLabel.right
        width: 100
        text: rotate_y
        onEditingFinished: rotate_y = parseFloat(text)
    }
    Label {
        id: zRotLabel
        anchors.top: xRotField.top
        anchors.left: yRotField.right
        text: "z:"
    }
    TextField {
        id: zRotField
        anchors.top: xRotField.top
        anchors.left: zRotLabel.right
        width: 100
        text: rotate_z
        onEditingFinished: rotate_z = parseFloat(text)
    }

    Label {
        id: angleLabel
        anchors.top: angleField.top
        anchors.left: parent.left
        text: "angle:"
    }
    TextField {
        id: angleField
        anchors.top: xRotField.bottom
        anchors.left: angleLabel.right
        text: rotate_angle
        onEditingFinished: rotate_angle = parseFloat(text)
    }
}
