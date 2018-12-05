import QtQuick 2.11
import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0

ExpandingWindow {

    property int componentIndex: 0

    title: "Component Editor"
    id: editComponentWindow
    minimumHeight: view.implicitHeight
    minimumWidth: view.implicitWidth

    Pane {
        id: viewContainer
        padding: 0
        anchors.fill: parent
        ListView {
            id: view
            implicitHeight: contentHeight
            anchors.fill: parent

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
            width: view.width

            onImplicitWidthChanged: view.implicitWidth = detailsPane.implicitWidth

            LabeledTextField {
                id: nameField
                labelText: "Name:"
                editorWidth: 200
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
                contentWidth: transformControls.implicitWidth
                anchors.left: parent.left
                anchors.right: parent.right
                TransformControls {
                    id: transformControls
                    transformModel: transform_model
                    componentIndex: editComponentWindow.componentIndex
                    anchors.left: parent.left
                    anchors.right: parent.right
                }
                Connections {
                    target: transform_model
                    onTransformsUpdated: components.transforms_updated(index)
                }
                states: State {
                    name: "hidden"; when: componentIndex == 0
                    PropertyChanges { target: transformFrame; height: 0 }
                    PropertyChanges { target: transformFrame; visible: false }
                    PropertyChanges { target: transformLabel; height: 0 }
                    PropertyChanges { target: transformLabel; visible: false }
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
