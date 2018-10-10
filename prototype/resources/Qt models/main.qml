import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Scene3D 2.0

Pane {
    width: 700
    height: 300
    padding: 5
    focus: true

    PixelControls {
        id: pixelFieldsArea
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        leftPadding: 0

        width: 365;
    }

    Frame {
        id: instrumentViewArea
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: pixelFieldsArea.right
        anchors.right: parent.right
        contentWidth: scene3d.implicitWidth
        contentHeight: scene3d.implicitHeight
        focus: true
        padding: 1

        Scene3D {
            id: scene3d
            anchors.fill: parent
            focus: true
            aspects: ["input", "logic"]
            cameraAspectRatioMode: Scene3D.AutomaticAspectRatio

            AnimatedEntity {}
        }

        MouseArea {
            anchors.fill: scene3d
            onClicked: instrumentViewArea.focus = true
            enabled: !instrumentViewArea.focus
        }
    }
}
