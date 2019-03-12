import QtQuick 2.11
import QtQuick.Controls 2.4
import MyValidators 1.0

Pane {

    contentWidth: Math.max(headingRow.implicitWidth, listContainer.implicitWidth)
    contentHeight: headingRow.implicitHeight + listContainer.implicitHeight

    Pane {
        id: headingRow
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        contentHeight: addComponentButton.height
        contentWidth: componentsLabel.width + addComponentButton.width
        padding: 1

        Label {
            id: componentsLabel
            anchors.left: parent.left
            anchors.verticalCenter: addComponentButton.verticalCenter
            text: "Components:"
        }
        Button {
            id: addComponentButton
            anchors.right: parent.right

            text: "Add component"
            onClicked: {
                if (windowLoader.source == ""){
                    windowLoader.source = "AddComponentWindow.qml"
                    window.positionChildWindow(windowLoader.item)
                    windowLoader.item.show()
                } else {
                    windowLoader.item.requestActivate()
                }
            }
            Loader {
                id: windowLoader
                Connections {
                    target: windowLoader.item
                    onClosing: windowLoader.source = ""
                }
                Connections {
                    target: window
                    onClosing: windowLoader.source = ""
                }
            }
        }
    }

    Frame {
        id: listContainer
        anchors.left: parent.left
        contentHeight: 100
        width: ComponentList.showScrollBar ? componentListView.implicitWidth - 10 : componentListView.implicitWidth
        anchors.top: headingRow.bottom
        anchors.bottom: parent.bottom
        padding: 3

        ListView {
            id: componentListView
            model: components
            delegate: componentDelegate
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical:           ScrollBar  {
            id: bar
            policy: ComponentList.showScrollBar ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
            active: true
        }

            onContentHeightChanged: {

                // Set a bool indicating that the content height in the component view has changed
                if (componentListView.contentHeight > componentListView.height) {
                    ComponentList.showScrollBar = true
                }
                else {
                    ComponentList.showScrollBar = false
                }
            }
        }

    }



    Component {
        id: componentDelegate
        Frame {
            id: componentBox
            padding: 5
            contentHeight: Math.max(mainContent.height, expansionCaret.height)
            contentWidth: Math.max(mainContent.implicitWidth, extendedContent.implicitWidth)
            width: ComponentList.showScrollBar ? componentListView.width - 10 : componentListView.width

            onImplicitWidthChanged: {
                if (componentListView.implicitWidth < componentBox.implicitWidth){
                    componentListView.implicitWidth = componentBox.implicitWidth
                }
            }

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
                implicitWidth: mainNameLabel.width + expansionCaret.width
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
                implicitWidth: extendedText.implicitWidth
                visible: false
                Item {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: nameField.height + transformControls.height + editorButton.height
                    implicitWidth: Math.max(nameField.implicitWidth,
                                            transformControls.implicitWidth,
                                            editorButton.implicitWidth + deleteButton.implicitWidth)
                    id: extendedText

                    LabeledTextField {
                        id: nameField
                        labelText: "Name:"
                        editorWidth: 200
                        editorText: name
                        onEditingFinished: name = editorText
                        validator: NameValidator {
                            model: components
                            myindex: index
                            onValidationFailed: {
                                nameField.ToolTip.show("Component names must be unique", 3000)
                            }
                        }
                    }

                    TransformControls {
                        id: transformControls
                        transformModel: transform_model
                        componentIndex: index
                        anchors.top: nameField.bottom
                        anchors.left: parent.left
                        anchors.right: parent.right
                    }
                    Connections {
                        target: transform_model
                        onTransformsUpdated: components.transforms_updated(index)
                    }
                    states: State {
                        name: "hidden"; when: index == 0
                        PropertyChanges { target: transformControls; height: 0 }
                        PropertyChanges { target: transformControls; visible: false }
                    }

                    PaddedButton {
                        id: editorButton
                        anchors.top: transformControls.bottom
                        anchors.left: parent.left
                        text: "Full editor"
                        onClicked: {
                            if (editorLoader.source == ""){
                                editorLoader.source = "EditComponentWindow.qml"
                                editorLoader.item.componentIndex = index
                                window.positionChildWindow(editorLoader.item)
                                editorLoader.item.show()
                            } else {
                                editorLoader.item.requestActivate()
                            }
                        }
                    }
                    Loader {
                        id: editorLoader
                        Connections {
                            target: editorLoader.item
                            onClosing: editorLoader.source = ""
                        }
                        Connections {
                            target: window
                            onClosing: editorLoader.source = ""
                        }
                    }
                    PaddedButton {
                        id: deleteButton
                        anchors.top: editorButton.top
                        anchors.right: parent.right
                        text: "Delete"
                        onClicked: components.remove_component(index)
                        buttonEnabled: removable
                        // The sample (at index 0) should never be removed. Don't even show it as an option.
                        visible: index != 0
                        ToolTip.visible: hovered & !removable
                        ToolTip.delay: 400
                        ToolTip.text: "Cannot remove a component that's in use as a transform parent"
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
