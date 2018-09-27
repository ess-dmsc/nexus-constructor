import QtQuick 2.11
import QtQuick.Scene3D 2.0

Rectangle {
    width: 700
    height: 300

    PixelControls {
        id: pixelFieldsArea
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left

        width: 355;
    }

    Rectangle {
        id: instrumentViewArea
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: pixelFieldsArea.right
        anchors.right: parent.right
        anchors.margins: 10
        border.width: 1
        border.color: "black"

        Scene3D {
            id: scene3d
            anchors.fill: parent
            anchors.margins: 1
            focus: true
            aspects: ["input", "logic"]
            cameraAspectRatioMode: Scene3D.AutomaticAspectRatio

            AnimatedEntity {}
        }
    }
}
