import QtQuick 2.12
import QtQuick.Controls 2.5

Text {
    property alias toolTipVisible: toolTip.visible
    property alias toolTipMessage: toolTip.text
    property alias containsMouse: mouseArea.containsMouse

    id: cross
    text: "×"
    font.bold: true
    color: "red"
    font.pointSize: 17

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
    }
    ToolTip {
        id: toolTip
        parent: mouseArea
    }
}