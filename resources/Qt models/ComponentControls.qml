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
            contentHeight: mainContent.height + extendedContent.height
            width: componentListView.width

            MouseArea {
                anchors.fill: parent
                onClicked: componentBox.state = (componentBox.state == "Extended") ? "" : "Extended"
            }

            Item {
                id: mainContent
                anchors.left: parent.left
                anchors.right: parent.right
                height: removalButton.height
                Label {
                    id: nameLabel
                    anchors.left: parent.left
                    anchors.top: parent.top
                    width: 100
                    text: "<b>Name:</b>" + name
                }
                Button {
                    id: removalButton
                    anchors.right: expansionCaret.left
                    anchors.rightMargin: 5
                    anchors.top: parent.top
                    text: "Remove"
                    objectName: "removalButton"
                    visible: index != 0
                    onClicked: components.remove_component(index)
                    background: Rectangle {
                        border.color: "#f00"
                        border.width: parent.pressed ? 2 : 1
                        radius: 8
                        // darker button when hovered-over, or tab-selected
                        color: (parent.hovered || parent.activeFocus) ? "#f88" : "#faa"
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
            }

            Item {
                id: extendedContent
                anchors.top: mainContent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 0
                visible: false
                Label {
                    id: extendedText
                    text: "I have been extended"
                }
            }

            states: State {
                name: "Extended"

                PropertyChanges { target: extendedContent; height: extendedText.height }
                PropertyChanges { target: extendedContent; visible: true }
                PropertyChanges { target: expansionCaret; rotation: 180 }
            }
        }
    }
}
