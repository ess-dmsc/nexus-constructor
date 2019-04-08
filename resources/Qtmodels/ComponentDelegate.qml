import QtQuick 2.12
import QtQuick.Controls 2.5
import MyValidators 1.0
import QtQuick.Layouts 1.11

Component {

    Frame {
        id: componentBox
        padding: 5
        contentHeight: Math.max(mainContent.height, expansionCaret.height)
        contentWidth: Math.max(mainContent.implicitWidth, extendedContent.implicitWidth)
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

            anchors.right: parent.right
            anchors.left: parent.left

            Item {
                id: mainContent
                height: mainNameLabel.height
                implicitWidth: mainNameLabel.width + expansionCaret.width
                Layout.fillHeight: false
                visible: true
                Label {
                    id: mainNameLabel
                    anchors.left: parent.left
                    anchors.top: parent.top
                    text: "Name:" + name
                }
            }
            Item {
                Layout.fillWidth: true
            }
            Image {
                id: expansionCaret
                Layout.maximumHeight: 20
                Layout.maximumWidth: 20
                source: "file:resources/images/caret.svg"
                transformOrigin: Item.Center
                Layout.fillHeight: false
                rotation: 0
            }
        }

        Item {

            id: extendedContent
            anchors.top: mainContent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: 0
            implicitWidth: transformControls.implicitWidth
            visible: false

            ColumnLayout {

                id: col
                anchors.right: parent.right
                anchors.left: parent.left
                anchors.top: parent.top

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

                    id: row
                    Layout.fillWidth: true

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
        }

        states: State {
            name: "Extended"

            PropertyChanges { target: mainContent; height: 0 }
            PropertyChanges { target: mainContent; visible: false }

            PropertyChanges { target: extendedContent; height: col.height }
            PropertyChanges { target: extendedContent; visible: true }

            PropertyChanges { target: componentBox; contentHeight: extendedContent.height}

            PropertyChanges { target: expansionCaret; rotation: 180 }
        }
    }
}