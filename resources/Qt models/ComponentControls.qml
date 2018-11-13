import QtQuick 2.11
import QtQuick.Controls 2.4
import MyValidators 1.0

Pane {

    Pane {
        id: headingRow
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        contentHeight: addDetector.height
        padding: 1

        Label {
            anchors.left: parent.left
            anchors.verticalCenter: addDetector.verticalCenter
            text: "Components:"
        }
        Button {
            id: addDetector
            anchors.right: parent.right

            text: "Add detector"
            onClicked: {
                modalLoader.source = "AddDetectorWindow.qml"
                modalLoader.item.show()
            }
            Loader {
                id: modalLoader
                Connections {
                    target: modalLoader.item
                    onClosing: modalLoader.source = ""
                }
            }
        }
    }

    Frame {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: headingRow.bottom
        anchors.bottom: parent.bottom
        padding: 1
        ListView {
            id: componentListView
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
                onClicked: componentBox.state = (componentBox.state == "Extended") ? "": "Extended"
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

            Item {
                id: extendedContent
                anchors.top: mainContent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 0
                visible: false
                Item {
                    height: nameField.height + transformControls.height + editorButton.height
                    width: parent.width
                    id: extendedText

                    LabeledTextField {
                        id: nameField
                        labelText: "Name:"
                        editorText: name
                        validator: NameValidator {
                            model: components
                            myindex: index
                        }
                    }

                    TransformControls {
                        id: transformControls
                        anchors.top: nameField.bottom
                    }

                    PaddedButton {
                        id: editorButton
                        anchors.top: transformControls.bottom
                        anchors.left: parent.left
                        width: parent.width / 4
                        text: "Full editor"
                    }
                    PaddedButton {
                        id: applyButton
                        anchors.top: editorButton.top
                        anchors.left: editorButton.right
                        width: parent.width / 4
                        text: "Apply changes"
                        onClicked: {
                            name = nameField.editorText
                            transformControls.saveFields()
                        }
                    }
                    PaddedButton {
                        id: discardButton
                        anchors.top: editorButton.top
                        anchors.left: applyButton.right
                        width: parent.width / 4
                        text: "Discard changes"
                        onClicked: {
                            nameField.editorText = name
                            transformControls.resetFields()
                        }
                    }
                    PaddedButton {
                        id: deleteButton
                        anchors.top: editorButton.top
                        anchors.left: discardButton.right
                        width: parent.width / 4
                        text: "Delete"
                        onClicked: components.remove_component(index)
                        enabled: removable
                        // The sample (at index 0) should never be removed. Don't even show it as an option.
                        visible: index != 0
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
