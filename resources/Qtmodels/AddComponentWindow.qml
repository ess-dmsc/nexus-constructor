import QtQuick 2.11
import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.11

ExpandingWindow {

    property string name: components.generate_component_name(componentType)
    property string description: ""
    property real transform_parent_index: 0
    property real dependent_transform_index: 0

    property int index: -1

    property string componentType: "Component"

    title: "Add " + componentType
    id: addComponentWindow
    minimumHeight: addComponentStack.implicitHeight
    minimumWidth: addComponentStack.implicitWidth

    Pane {
        id: contentPane
        anchors.fill: parent
        padding: 0

        StackLayout {
            id: addComponentStack
            anchors.fill: parent
            currentIndex: 0

            Pane {
                id: setupPane

                property var selectedType
                property string geometryState
                property string pixelState

                ColumnLayout {
                    anchors.fill: parent

                    Label {
                        id: typeLabel
                        text: "Component type:"
                    }

                    Pane {
                        id: typePane

                        ComboBox {
                            id: typePicker
                            model: componentTypeModel
                            textRole: "name"
                            onActivated: updateBackend()
                            Component.onCompleted: updateBackend()

                            function updateBackend() {
                                setupPane.selectedType = componentTypeModel.get(typePicker.currentIndex)
                                pixelPane.checkFirstEnabled()
                            }
                        }
                    }

                Label {
                    id: geometryLabel
                    text: "Geometry:"
                }
                Pane {
                    id: geometryPane
                    Layout.fillWidth: true

                    RowLayout {
                        id: radioButtonRow

                        RadioButton {
                            id: meshRadio
                            text: "Mesh"
                            onClicked: {
                                setupPane.geometryState = "OFF"
                                GeometryFileSelected.geometryFileSelected = false
                                pixelPane.checkFirstEnabled()
                            }

                                checked: true
                                Component.onCompleted: setupPane.geometryState = "OFF"
                            }
                            RadioButton {
                                id: cylinderRadio
                                text: "Cylinder"
                                onClicked: {
                                    setupPane.geometryState = "Cylinder"
                                    pixelPane.checkFirstEnabled()
                                }
                            }
                            RadioButton {
                                id: noShapeRadio
                                text: "None"
                                onClicked: {
                                    setupPane.geometryState = "None"
                                    setupPane.pixelState = ""
                                    pixelPane.checkFirstEnabled()
                                }
                            }
                        }
                    }

                    Label {
                        id: pixelLabel
                        text: "Pixels:"
                        enabled: !noShapeRadio.checked
                    }
                    Pane {
                        id: pixelPane
                        enabled: !noShapeRadio.checked

                        function checkFirstEnabled(){
                            var buttons = [singlePixelRadio, pixelGridRadio, mappedMeshRadio, noPixelRadio]
                            for (var i = 0; i < buttons.length; i++) {
                                if (buttons[i].enabled){
                                    buttons[i].checked = true
                                    return
                                }
                            }
                        }
                        ColumnLayout {

                            RadioButton {
                                id: singlePixelRadio
                                text: "Single ID"
                                enabled: setupPane.selectedType.allowSingleID
                                onCheckedChanged: if (checked) setupPane.pixelState = "SinglePixel"
                            }
                            RadioButton {
                                id: pixelGridRadio
                                text: "Repeatable grid"
                                enabled: setupPane.selectedType.allowPixelGrid
                                onCheckedChanged: if (checked) setupPane.pixelState = "Grid"
                            }
                            RadioButton {
                                id: mappedMeshRadio
                                text: "Face mapped mesh"
                                enabled: setupPane.selectedType.allowMappedMesh && meshRadio.checked
                                onCheckedChanged: if (checked) setupPane.pixelState = "Mapping"
                            }
                            RadioButton {
                                id: noPixelRadio
                                text: "None"
                                enabled: setupPane.selectedType.allowNoPixels
                                onCheckedChanged: if (checked) setupPane.pixelState = ""
                            }
                        }
                    }

                    PaddedButton {
                        id: continueButton
                        text: "Continue"
                        onClicked: {
                            componentType = setupPane.selectedType.name
                            pixelControls.state = setupPane.pixelState
                            geometryControls.state = setupPane.geometryState
                            contentPane.contentHeight = detailsPane.implicitHeight
                            contentPane.contentWidth = detailsPane.implicitWidth
                            detailsPane.focus = true
                            nameField.focus = true
                            addComponentStack.currentIndex = 1
                        }
                    }

                    ListModel {
                        id: componentTypeModel
                        ListElement {
                            name: "Detector"
                            allowSingleID: false
                            allowPixelGrid: true
                            allowMappedMesh: true
                            allowNoPixels: false
                        }
                        ListElement {
                            name: "Monitor"
                            allowSingleID: true
                            allowPixelGrid: false
                            allowMappedMesh: false
                            allowNoPixels: false
                        }
                        ListElement {
                            name: "Source"
                            allowSingleID: false
                            allowPixelGrid: false
                            allowMappedMesh: false
                            allowNoPixels: true
                        }
                        ListElement {
                            name: "Slit"
                            allowSingleID: false
                            allowPixelGrid: false
                            allowMappedMesh: false
                            allowNoPixels: true
                        }
                        ListElement {
                            name: "Moderator"
                            allowSingleID: false
                            allowPixelGrid: false
                            allowMappedMesh: false
                            allowNoPixels: true
                        }
                        ListElement {
                            name: "Disk Chopper"
                            allowSingleID: false
                            allowPixelGrid: false
                            allowMappedMesh: false
                            allowNoPixels: true
                        }
                    }
                }
            }

            Pane {
                id: detailsPane
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: false

                ColumnLayout {
                    id: detailColumn
                    anchors.fill: parent

                    GridLayout {
                        rows: 2
                        columns: 2
                        Layout.fillWidth: true
                        Label {
                            text: "Name: "
                        }
                        TextField {
                            id: nameField
                            text: name
                            onEditingFinished: name = text
                            Layout.fillWidth: true
                            selectByMouse: true
                            validator: NameValidator {
                                model: components
                                myindex: -1
                                onValidationFailed: {
                                    nameField.ToolTip.show(ErrorMessages.repeatedComponentName, 3000)
                                }
                            }
                        }

                        Label {
                            text: "Description: "
                        }
                        TextField {
                            id: descriptionField
                            text: description
                            onEditingFinished: description = text
                            Layout.fillWidth: true
                            selectByMouse: true
                        }
                    }

                    Label {
                        id: transformLabel
                        text: "Transform:"
                        Layout.fillWidth: true
                    }

                    Frame {
                        id: transformFrame
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: transformControls.implicitHeight
                        TransformControls {
                            id: transformControls
                            transformModel: TransformationModel {}
                            componentIndex: index
                            anchors.fill: parent
                        }
                    }

                    GeometryControls {
                        id: geometryControls
                        Layout.fillWidth: true
                        onMeshChanged: pixelControls.restartMapping(geometryControls.geometryModel)
                    }

                    PixelControls {
                        id: pixelControls
                        visible: state != ""
                        Layout.fillWidth: true
                    }

                    PaddedButton {
                        id: addButton
                        leftPadding: 0
                        text: "Add"
                        Layout.fillWidth: false
                        buttonEnabled: {
                            // Grey-out the Add button for Cylinder geometries if the units are invalid
                            setupPane.geometryState != "Cylinder" || (setupPane.geometryState == "Cylinder" && ValidUnits.validCylinderUnits)
                        }
                        onClicked: {
                            if (setupPane.geometryState == "OFF" && GeometryFileSelected.geometryFileSelected == false) {
                                noGeometryFileDialog.open()
                            }
                            else {
                                components.add_component(componentType, name, description, transform_parent_index, dependent_transform_index,
                                                         geometryControls.geometryModel,
                                                         pixelControls.pixelModel,
                                                         transformControls.transformModel)

                                addComponentWindow.close()

                                // Reset the booleans for input validity
                                resetUnitChecks()

                            }
                        }
                    }
                }
                MessageDialog {
                    id: noGeometryFileDialog
                    icon: StandardIcon.Critical
                    title: "No Geometry File Given."
                    text: "No Geometry file given. Please select a geometry file in order to create a mesh."
                    visible: false
                }
            }
        }
    }

    function resetUnitChecks() {
        ValidUnits.validCylinderUnits = false
    }

    onClosing: {
        resetUnitChecks()
    }
}
