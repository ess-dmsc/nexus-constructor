import QtQuick 2.11
import QtQuick.Window 2.11
import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0

Window {

    property string name: components.generate_component_name(componentType)
    property string description: ""
    property real transform_parent_index: 0
    property real rotate_x: 0
    property real rotate_y: 0
    property real rotate_z: 1
    property real rotate_angle: 0
    property real translate_x: 0
    property real translate_y: 0
    property real translate_z: 0

    property int index: -1

    property string componentType: "Component"

    title: "Add " + componentType
    id: addComponentWindow
    minimumHeight: contentPane.height
    minimumWidth: contentPane.width
    height: minimumHeight
    width: minimumWidth
    maximumHeight: minimumHeight
    maximumWidth: minimumWidth

    Pane {
        id: contentPane
        contentWidth: geometrySelectionPane.width
        contentHeight: geometrySelectionPane.height
        padding: 0

        Pane {
            id: geometrySelectionPane
            contentWidth: Math.max(detectorPane.width,
                                   generalComponentPane.width)
            contentHeight: detectorLabel.height + detectorPane.height +
                           generalComponentLabel.height + generalComponentPane.height
            visible: true

            Label {
                id: detectorLabel
                text: "Detector:"
            }

            Pane {
                id: detectorPane
                anchors.top: detectorLabel.bottom
                contentHeight: offDetectorButton.height
                contentWidth: offDetectorButton.width + cylinderDetectorButton.width + mappedMeshButton.width

                PaddedButton {
                    id: offDetectorButton
                    anchors.top: parent.top
                    text: "Repeatable Mesh"
                    onClicked: {
                        geometryControls.state = "OFF"
                        pixelControls.state = "Grid"
                        componentType = "Detector"
                        contentPane.state = "EnterDetails"
                    }
                }

                PaddedButton {
                    id: cylinderDetectorButton
                    anchors.top: offDetectorButton.top
                    anchors.left: offDetectorButton.right
                    text: "Repeatable Cylinder"
                    onClicked: {
                        geometryControls.state = "Cylinder"
                        pixelControls.state = "Grid"
                        componentType = "Detector"
                        contentPane.state = "EnterDetails"
                    }
                }

                PaddedButton {
                    id: mappedMeshButton
                    anchors.top: offDetectorButton.top
                    anchors.left: cylinderDetectorButton.right
                    text: "Pixel-Face Mapped Mesh"
                    onClicked: {
                        geometryControls.state = "OFF"
                        pixelControls.state = "Mapping"
                        componentType = "Detector"
                        contentPane.state = "EnterDetails"
                    }
                }
            }

            Label {
                id: generalComponentLabel
                anchors.top: detectorPane.bottom
                text: "General Components:"
            }

            Pane {
                id: generalComponentPane
                anchors.top: generalComponentLabel.bottom
                contentHeight: typePicker.height + meshButton.height
                contentWidth: Math.max(typeLabel.width + typePicker.width,
                                       geometryLabel.width + meshButton.width + cylinderButton.width)

                Label {
                    id: typeLabel
                    anchors.left: parent.left
                    anchors.verticalCenter: typePicker.verticalCenter
                    text: "Component type:"
                }
                ComboBox {
                    id: typePicker
                    anchors.left: typeLabel.right
                    anchors.top: parent.top
                    model: componentTypeModel
                    textRole: "name"
                }

                Label {
                    id: geometryLabel
                    anchors.left: parent.left
                    anchors.verticalCenter: meshButton.verticalCenter
                    text: "Geometry:"
                }
                PaddedButton {
                    id: meshButton
                    anchors.top: typePicker.bottom
                    anchors.left: geometryLabel.right
                    text: "Mesh"
                    onClicked: {
                        var selectedType = componentTypeModel.get(typePicker.currentIndex)
                        geometryControls.state = "OFF"
                        pixelControls.state = selectedType.pixelState
                        componentType = selectedType.name
                        contentPane.state = "EnterDetails"
                    }
                }
                PaddedButton {
                    id: cylinderButton
                    anchors.top: meshButton.top
                    anchors.left: meshButton.right
                    text: "Cylinder"
                    onClicked: {
                        var selectedType = componentTypeModel.get(typePicker.currentIndex)
                        geometryControls.state = "Cylinder"
                        pixelControls.state = selectedType.pixelState
                        componentType = selectedType.name
                        contentPane.state = "EnterDetails"
                    }
                }

                ListModel {
                    id: componentTypeModel
                    ListElement {
                        name: "Monitor"
                        pixelState: "SinglePixel"
                    }
                    ListElement {
                        name: "Source"
                        pixelState: ""
                    }
                }
            }
        }

        Pane {
            id: detailsPane
            contentWidth:  Math.max(transformFrame.implicitWidth, geometryControls.implicitWidth, pixelControls.implicitWidth)
            contentHeight: nameField.height
                           + descriptionField.height
                           + transformLabel.height
                           + transformFrame.height
                           + geometryControls.height
                           + pixelControls.height
                           + addButton.height
            visible: false

            LabeledTextField {
                id: nameField
                labelText: "Name:"
                editorText: name
                onEditingFinished: name = editorText
                validator: NameValidator {
                    model: components
                    myindex: -1
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
                    anchors.left: parent.left
                    anchors.right: parent.right
                }
            }

            GeometryControls {
                id: geometryControls
                anchors.top: transformFrame.bottom
                anchors.right:parent.right
                anchors.left: parent.left
                onMeshChanged: pixelControls.restartMapping(geometryControls.geometryModel)
            }

            PixelControls {
                id: pixelControls
                anchors.top: geometryControls.bottom
                anchors.right:parent.right
                anchors.left: parent.left
                visible: state != ""
            }

            PaddedButton {
                id: addButton
                anchors.top: pixelControls.bottom
                anchors.left: parent.left
                leftPadding: 0
                text: "Add"
                onClicked: {
                    components.add_component(componentType, name, description, transform_parent_index,
                                             translate_x, translate_y, translate_z,
                                             rotate_x, rotate_y, rotate_z, rotate_angle,
                                             geometryControls.geometryModel,
                                             pixelControls.pixelModel)
                    addComponentWindow.close()
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
                PropertyChanges { target: contentPane; contentHeight: detailsPane.height }
                PropertyChanges { target: contentPane; contentWidth: detailsPane.width }
                PropertyChanges { target: detailsPane; focus: true}
                PropertyChanges { target: nameField; focus: true}
            }
        ]
    }
}
