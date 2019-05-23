import QtQuick 2.12
import QtQuick.Controls 2.5

Text {
    property alias toolTipMessage: toolTip.text

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
        visible: cross.visible && cross.opacity && mouseArea.containsMouse
    }
}
