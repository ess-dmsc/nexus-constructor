import QtQuick 2.11
import QtQuick.Window 2.11
import QtQuick.Controls 2.4
import MyModels 1.0

Window {

    property InstrumentModel components
    title: "Add Detector"
    id: addDetectorWindow
    modality: Qt.ApplicationModal
    width: 200
    height: 200

    Pane {
        anchors.fill: parent
        
        Text {
            id: countText
            text: "Component count:" + components.rowCount()
        }

        Button {
            anchors.top: countText.bottom
            text: "Add detector"
            onClicked: {
                components.add_detector("From popup button")
            }
        }
    }
}
