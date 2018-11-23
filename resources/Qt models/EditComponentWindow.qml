import QtQuick 2.11
import QtQuick.Window 2.11
import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0

Window {

    property int componentIndex: 0

    title: "Component Editor"
    id: editComponentWindow
    modality: Qt.ApplicationModal
    minimumHeight: view.height
    minimumWidth: view.width
    height: minimumHeight
    width: minimumWidth
    maximumHeight: minimumHeight
    maximumWidth: minimumWidth

    Pane {
        id: viewContainer
        padding: 0
        anchors.fill: parent
        ListView {
            id: view
            height: contentHeight
            model: component
            delegate: editorDelegate
            interactive: false
        }
    }

    SingleComponentModel {
        id: component
        model: components
        index: componentIndex
    }

    Component {
        id: editorDelegate
        Pane {
            id: detailsPane
            contentWidth: Math.max(transformFrame.implicitWidth, geometryControls.implicitWidth, pixelControls.implicitWidth)
            contentHeight: nameField.height
                           + descriptionField.height
                           + transformLabel.height
                           + transformFrame.height
                           + geometryControls.height
                           + pixelControls.height

            Component.onCompleted: view.width = detailsPane.width

            LabeledTextField {
                id: nameField
                labelText: "Name:"
                editorText: name
                onEditingFinished: name = editorText
                validator: NameValidator {
                    model: components
                    myindex: componentIndex
                    onValidationFailed: {
                        nameField.ToolTip.show("Component names must be unique", 3000)
                    }
                }
            }

            LabeledTextField {
                id: descriptionField
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: nameField.bottom
                anchoredEditor: true
                labelText: "Description:"
                editorText: description
                onEditingFinished: description = editorText
            }

            Label {
                id: transformLabel
                anchors.top: descriptionField.bottom
                anchors.left: parent.left
                text: "Transform:"
            }

            Frame {
                id: transformFrame
                anchors.top: transformLabel.bottom
                contentHeight: transformControls.height
                contentWidth: transformControls.width
                TransformControls {
                    id: transformControls
                }
            }

            GeometryControls {
                id: geometryControls
                anchors.top: transformFrame.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                state: geometry_state

                Component.onCompleted: geometryControls.geometryModel.set_geometry(componentIndex, components)
                onMeshChanged: {
                    pixelControls.restartMapping(geometryControls.geometryModel)
                    components.update_mesh(componentIndex)
                }
                onCylinderChanged: components.update_mesh(componentIndex)
            }

            PixelControls {
                id: pixelControls
                anchors.top: geometryControls.bottom
                anchors.right:parent.right
                anchors.left: parent.left
                width: parent.contentWidth
                state: pixel_state
                visible: pixel_state != ""

                Component.onCompleted:{
                    if (pixel_state != "") {
                        pixelControls.pixelModel.set_pixel_model(componentIndex, components)
                    }
                }
                onLayoutChanged: components.update_mesh(componentIndex)
            }
        }
    }
}
