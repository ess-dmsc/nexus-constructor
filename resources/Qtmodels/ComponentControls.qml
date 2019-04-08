import QtQuick 2.11
import QtQuick.Controls 2.4
import MyValidators 1.0
import QtQuick.Layouts 1.11

Pane {

    contentWidth: mainCol.implicitWidth
    contentHeight: mainCol.implicitHeight

    ColumnLayout {

        id: mainCol
        anchors.fill: parent

        RowLayout {

            id: headingRow
            Layout.fillWidth: true
            Layout.fillHeight: false

            Label {
                id: componentsLabel
                text: "Components:"
            }
            Item {
                Layout.fillWidth: true
            }
            Button {
                id: addComponentButton

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

            contentWidth: componentListView.implicitWidth
            Layout.fillWidth: true
            Layout.fillHeight: true
            padding: 1

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

    ComponentDelegate {
        id: componentDelegate
    }
}
