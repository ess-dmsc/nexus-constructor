import QtQuick 2.11
import QtQuick.Controls 2.4
import MyValidators 1.0
import QtQuick.Layouts 1.11

Pane {

    contentWidth: componentControlsColumn.implicitWidth
    contentHeight: componentControlsColumn.implicitHeight

    ColumnLayout {
        id: componentControlsColumn
        anchors.fill: parent

        RowLayout {
            id: headingRow

            Label {
                id: componentsLabel
                text: "Components: "
            }
            Item {
                // Spacer Item to force Components label and Add Component button to opposite ends of pane
                Layout.fillWidth: true
            }
            Button {
                id: addComponentButton
                text: "Add Component"
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
            contentWidth: componentListView.implicitWidth
            contentHeight: 100
            padding: 1
            Layout.fillHeight: true

            ListView {
                id: componentListView
                model: components
                delegate: componentDelegate
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: bar
            }
            ActiveScrollBar {
                // Place scrollbar outside of ListView so that it doesn't overlap with ListView contents
                id: bar
                anchors.left: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
            }
        }
    }

    Component {
        id: componentDelegate
        Frame {
            id: componentBox
            padding: 5
            contentHeight: expansionCaret.height
            contentWidth: extendedContent.implicitWidth
            width: componentListView.width

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

            RowLayout {
                id: shortenedContent
                anchors.fill: parent

                Label {
                    id: mainNameLabel
                    text: "Name:" + name
                }
                Item {
                    Layout.fillWidth: true
                }
                Image {
                    id: expansionCaret
                    Layout.preferredWidth: 20
                    Layout.preferredHeight: 20
                    source: "file:resources/images/caret.svg"
                    transformOrigin: Item.Center
                    rotation: 0
                }
            }
            ColumnLayout {
                id: extendedContent
                implicitWidth: transformControls.implicitWidth
                anchors.left: parent.left
                anchors.right: parent.right
                visible: false
                // height: 0

                RowLayout {
                    Label {
                        text: "Name: "
                    }
                    TextField {
                        id: nameField
                        text: name
                        onEditingFinished: name = text
                        validator: NameValidator {
                            model: components
                            myindex: index
                            onValidationFailed: {
                                nameField.ToolTip.show(ErrorMessages.repeatedComponentName, 3000)
                            }
                        }
                        Layout.fillWidth: true
                    }
                    Image {
                        id: expansionCaret2
                        Layout.preferredWidth: 20
                        Layout.preferredHeight: 20
                        source: "file:resources/images/caret.svg"
                        transformOrigin: Item.Center
                        rotation: 180
                    }
                }
                TransformControls {
                    id: transformControls
                    transformModel: transform_model
                    componentIndex: index
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

                RowLayout {
                    PaddedButton {
                        id: editorButton
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
                    Item {
                        Layout.fillWidth: true
                    }
                    PaddedButton {
                        id: deleteButton
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

                PropertyChanges { target: shortenedContent; height: 0 }
                PropertyChanges { target: shortenedContent; visible: false }

                // PropertyChanges { target: extendedContent; height: extendedCon.height }
                PropertyChanges { target: extendedContent; visible: true }

                PropertyChanges { target: componentBox; contentHeight: extendedContent.height}

                // PropertyChanges { target: expansionCaret; rotation: 180 }
                PropertyChanges { target: expansionCaret; visible: false }
            }
        }
    }
}
