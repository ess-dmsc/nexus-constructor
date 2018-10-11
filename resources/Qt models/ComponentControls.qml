import QtQuick 2.11
import QtQuick.Controls 2.4

Pane {

    Pane {
        id: textRow
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        contentHeight: addDetector.height
        padding: 1

        Label {
            id: nameLabel
            anchors.left: parent.left
            anchors.verticalCenter: addDetector.verticalCenter
            text: "Components:"
        }
        Button {
            id: addDetector
            objectName: "addDetector"
            anchors.right: parent.right

            text: "Add detector"
            onClicked: {
                myLogger.log("Adding detector")
                components.add_detector("A detector")
            }
        }
    }

    Frame {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: textRow.bottom
        anchors.bottom: parent.bottom
        padding: 1
        ListView {
            id: componentListView
            objectName: "componentListView"
            model: components
            delegate: componentDelegate
            anchors.fill: parent
            clip: true
        }
    }

    Component {
        id: componentDelegate
        Frame {
            id: componentBox
            padding: 5
            contentHeight: Math.max(mainContent.height, expansionCaret.height)
            width: componentListView.width

            MouseArea {
                id: expansionClickArea
                anchors.fill: parent
                onClicked: {
                    if (componentBox.state == "Extended") {
                        componentBox.state = ""
                    } else {
                        componentBox.state = "Extended"
                    }
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

            Item {
                id: mainContent
                anchors.left: parent.left
                anchors.right: parent.right
                height: mainNameLabel.height
                visible: true
                Label {
                    id: mainNameLabel
                    anchors.left: parent.left
                    anchors.top: parent.top
                    text: "Name:" + name
                }
            }

            // Set the update listener on the combobox!
            Item {
                id: extendedContent
                anchors.top: mainContent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 0
                visible: false
                Item {
                    height: nameField.height +
                        relativePicker.height +
                        translateLabel.height +
                        xField.height +
                        rotateLabel.height +
                        xRotField.height +
                        angleField.height +
                        editorButton.height
                    width: parent.width
                    id: extendedText

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

                    Button{
                        id: editorButton
                        anchors.top: angleField.bottom
                        anchors.left: parent.left
                        text: "Full editor"
                    }
                    Button{
                        id: discardButton
                        anchors.top: editorButton.top
                        anchors.left: editorButton.right
                        text: "Discard changes"
                    }
                    Button{
                        id: deleteButton
                        anchors.top: editorButton.top
                        anchors.left: discardButton.right
                        text: "Delete"
                        onClicked: components.remove_component(index)
                    }
                }
            }

            states: State {
                name: "Extended"

                PropertyChanges { target: mainContent; height: 0 }
                PropertyChanges { target: mainContent; visible: false }

                PropertyChanges { target: extendedContent; height: extendedText.height }
                PropertyChanges { target: extendedContent; visible: true }

                PropertyChanges { target: componentBox; contentHeight: extendedContent.height}

                PropertyChanges { target: expansionCaret; rotation: 180 }
            }
        }
    }
}
