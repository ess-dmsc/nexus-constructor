import QtQuick 2.11
import QtQuick.Window 2.11
import QtQuick.Controls 2.4
import MyModels 1.0

Window {

    property string name: "Detector"
    property string description: ""
    property real transform_parent_index: 0
    property real rotate_x: 0
    property real rotate_y: 0
    property real rotate_z: 1
    property real rotate_angle: 0
    property real translate_x: 0
    property real translate_y: 0
    property real translate_z: 0

    title: "Add Detector"
    id: addDetectorWindow
    modality: Qt.ApplicationModal
    width: 200
    height: 200

    Pane {
        id: contentPane
        anchors.fill: parent

        Pane {
            id: geometrySelectionPane
            anchors.fill: parent
            visible: true

            Button {
                id: offButton
                text: "Repeatable OFF"
                onClicked: {
                    geometryControls.state = "OFF"
                    contentPane.state = "EnterDetails"
                }
            }

            Button {
                id: cylinderButton
                anchors.top: offButton.bottom
                text: "Repeatable Cylinder"
                onClicked: {
                    geometryControls.state = "Cylinder"
                    contentPane.state = "EnterDetails"
                }
            }
        }

        Pane {
            id: detailsPane
            anchors.fill: parent
            visible: false

            LabeledTextField {
                id: nameField
                labelText: "Name:"
                editorText: name
                onEditingFinished: name = editorText
            }

            LabeledTextField {
                id: descriptionField
                anchors.left: parent.left
                anchors.top: nameField.bottom
                labelText: "Description:"
                editorText: description
                onEditingFinished: description = editorText
            }

            Label {
                id: transformLabel
                anchors.top: descriptionField.bottom
                anchors.left: parent.left
                text: "Transform"
            }

            Frame {
                id: transformFrame
                anchors.top: transformLabel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                contentHeight: transformControls.height
                TransformControls {
                    id: transformControls
                }
            }

            GeometryControls {
                id: geometryControls
                anchors.top: transformFrame.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: addButton.top
            }

            Button {
                id: addButton
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                text: "Add"
                onClicked: {
                    transformControls.saveFields()
                    components.add_detector(name, description, transform_parent_index,
                                            translate_x, translate_y, translate_z,
                                            rotate_x, rotate_y, rotate_z, rotate_angle)
                    components.set_geometry(components.rowCount() - 1, geometryControls.geometryModel)
                    addDetectorWindow.close()
                }
            }
        }

        states: [
            State {
                name: "PickGeometryType"
            },
            State {
                name: "EnterDetails"

                PropertyChanges { target: geometrySelectionPane; visible: false }
                PropertyChanges { target: detailsPane; visible: true }
                PropertyChanges { target: addDetectorWindow; height: 400 }
                PropertyChanges { target: addDetectorWindow; width: 400 }
            }
        ]
    }
}
