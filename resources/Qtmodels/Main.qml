import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Scene3D 2.0
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.11
import MyJson 1.0
import MyModels 1.0



        RowLayout {
            id: centralRow
//            anchors.fill: parent
//            Layout.minimumWidth: 100

//            ComponentControls {
//                id: componentFieldsArea
//                leftPadding: 0
//                Layout.fillHeight: true
//                Layout.fillWidth: false
//            }

            Frame {
                id: instrumentViewArea
//                leftPadding:0
                contentWidth: 500
                contentHeight: 500
                Layout.fillHeight: true
                Layout.fillWidth: true
                focus: true
//                padding: 1

                Scene3D {
                    id: scene3d
                    anchors.fill: parent
                    focus: true
                    aspects: ["input", "logic"]
                    cameraAspectRatioMode: Scene3D.AutomaticAspectRatio

                    AnimatedEntity {
                        id: instrumentEntity
                        instrument: components
                    }
                }

                AxisIndicator {
                    id: axisIndicator
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    width: 100
                    height: 100

                    targetCamera: instrumentEntity.camera
                }

                MouseArea {
                    anchors.fill: scene3d
                    onClicked: instrumentViewArea.focus = true
                    enabled: !instrumentViewArea.focus
                }
            }
            NexusModel {
        id: nxsModel
    }

    InstrumentModel{
        id: components
        Component.onCompleted: {
            initialise(nxsModel.entryGroup)
        }
    }
        }








