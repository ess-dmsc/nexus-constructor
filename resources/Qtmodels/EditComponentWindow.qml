import QtQuick 2.11
import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0
import QtQuick.Layouts 1.11

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
            contentWidth: editorColumn.implicitWidth
            contentHeight: editorColumn.implicitHeight
            width: view.width
            height: viewContainer.height
            onImplicitWidthChanged: view.implicitWidth = detailsPane.implicitWidth
            onImplicitHeightChanged: view.implicitHeight = detailsPane.implicitHeight

            GridLayout {
                id: editorColumn
                anchors.fill: parent
                rows: 5
                columns: 3

                Label {
                    text: "Name: "
                }
                TextField {
                    id: nameField
                    Layout.fillWidth: true
                    Layout.preferredWidth: 200
                    text: name
                    onEditingFinished: name = text
                    validator: NameValidator {
                        model: components
                        myindex: componentIndex
                        onValidationFailed: {
                            repeatedNameCross.opacity = 1
                        }
                        onValidationSuccess: {
                            repeatedNameCross.opacity = 0
                        }
                    }
                }
                InvalidInputCross {
                    id: repeatedNameCross
                    toolTipMessage: ErrorMessages.repeatedComponentName
                    Layout.fillWidth: false
                }
                Label {
                    text: "Description: "
                }
                TextField {
                    id: descriptionField
                    Layout.fillWidth: true
                    text: description
                    onEditingFinished: description = text
                    Layout.columnSpan: 2
                }
                Label {
                    id: transformLabel
                    text: "Transform:"
                    Layout.columnSpan: 3
                }

                Frame {
                    id: transformFrame
                    Layout.columnSpan: 3
                    contentHeight: transformControls.implicitHeight
                    contentWidth: transformControls.implicitWidth
                    Layout.fillWidth: true
                    TransformControls {
                        id: transformControls
                        transformModel: transform_model
                        componentIndex: editComponentWindow.componentIndex
                        anchors.fill: parent
                    }
                    Connections {
                        target: transform_model
                        onTransformsUpdated: components.transforms_updated(index)
                    }
                    states: State {
                        name: "hidden"; when: componentIndex == 0
                        PropertyChanges { target: transformFrame; implicitHeight: 0 }
                        PropertyChanges { target: transformFrame; visible: false }
                        PropertyChanges { target: transformLabel; height: 0 }
                        PropertyChanges { target: transformLabel; visible: false }
                        PropertyChanges { target: editComponentWindow; height: minimumHeight}
                    }
                }
                GeometryControls {
                    id: geometryControls
                    state: geometry_state
                    Layout.columnSpan: 3
                    Layout.fillWidth: true
                    Component.onCompleted: {
                        geometryControls.geometryModel.set_geometry(componentIndex, components)
                    }
                    onMeshChanged: {
                        pixelControls.restartMapping(geometryControls.geometryModel)
                        components.update_mesh(componentIndex)
                    }
                    onCylinderChanged: components.update_mesh(componentIndex)
                }
                PixelControls {
                    id: pixelControls
                    state: pixel_state
                    visible: pixel_state != ""
                    Layout.columnSpan: 3
                    Layout.fillWidth: true

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
}
