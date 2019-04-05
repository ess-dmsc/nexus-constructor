import QtQuick.Controls 2.5
import QtQuick 2.12
import QtQuick.Layouts 1.11

Pane {

    contentWidth: 300

    ColumnLayout {

        anchors.fill: parent

        ListView {
            id: jsonListView
            model: jsonModel
            delegate: jsonLineDelegate
            Layout.fillHeight: true
            Layout.fillWidth: true
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AlwaysOn
            }
        }

        Button {
            id: copyButton
            text: "Copy to Clipboard"
            Layout.maximumHeight: 20
            Layout.minimumHeight: 20
            Layout.fillWidth: true
            onClicked: {

                // Filewriter mode - Copy the Filewriter JSON to the clipboard
                if (jsonMode == "liveFW") {
                    jsonConnector.copy_nexus_filewriter_json_to_clipboard(components)
                }

                // Nexus Constructor mode - Copy the Nexus Constructor JSON to the clipboard
                if (jsonMode == "liveGC") {
                    jsonConnector.copy_nexus_constructor_json_to_clipboard(components)
                }
            }
        }

        Component {
            id: jsonLineDelegate
            Label {
                id: jsonText
                text: (collapsed ? collapsed_text : full_text)
                font.family: "Courier New"
                wrapMode: Text.Wrap
                width: parent.width
                MouseArea {
                    anchors.fill: parent
                    onClicked: collapsed = !collapsed
                }
            }
        }

        states: State {
            name: "hidden"; when: jsonMode == "hidden"
            PropertyChanges { target: jsonPane; visible: false }
            PropertyChanges { target: jsonPane; width: 0 }
        }
    }
}