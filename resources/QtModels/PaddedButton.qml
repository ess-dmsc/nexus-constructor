import QtQuick 2.11
import QtQuick.Controls 2.4


Pane {
    property alias text: button.text
    property alias buttonEnabled: button.enabled
    id: pane
    padding: 2
    signal clicked

    Button {
        id: button
        anchors.fill: parent
        onClicked: pane.clicked()
    }
}
