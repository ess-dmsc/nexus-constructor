import QtQuick 2.11
import QtQuick.Controls 2.4


Pane {
    property string text: ""
    property bool buttonEnabled: true
    id: pane
    padding: 2
    signal clicked

    Button {
        id: button
        anchors.fill: parent
        text: pane.text
        enabled: buttonEnabled
        onClicked: pane.clicked()
    }
}
