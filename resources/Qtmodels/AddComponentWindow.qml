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
    minimumHeight: contentPane.implicitHeight
    minimumWidth: contentPane.implicitWidth

    Pane {

        id: contentPane
        contentWidth: setupPane.implicitWidth
        contentHeight: setupPane.implicitHeight
        anchors.fill: parent
        padding: 0

        Pane {

            id: setupPane
            contentHeight: col.height
            contentWidth: col.width

            property var selectedType
            property string geometryState
            property string pixelState

            ColumnLayout {

                id: col

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
                    contentWidth: geometryButtonRow.width
                    contentHeight: Math.max(meshRadio.height, cylinderRadio.height)

                    RowLayout {

                        id: geometryButtonRow

                        RadioButton {
                            id: meshRadio
                            text: "Mesh"
                            onClicked: {
                                setupPane.geometryState = "OFF"
                                GeometryFileSelected.geometryFileSelected = false
                            }

                            checked: true
                            Component.onCompleted: setupPane.geometryState = "OFF"
                        }
                        RadioButton {
                            id: cylinderRadio
                            text: "Cylinder"
                            onClicked: {
                                setupPane.geometryState = "Cylinder"
                                if (mappedMeshRadio.checked) {
                                    pixelPane.checkFirstEnabled()
                                }
                            }
                        }
                        RadioButton {
                            id: noShapeRadio
                            text: "None"
                            onClicked: setupPane.geometryState = "None", setupPane.pixelState = ""
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

                    Layout.fillWidth: true
                    contentHeight: pixelTypes.height
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

                        id: pixelTypes

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
                        detailsPane.pixelControlsState = setupPane.pixelState
                        detailsPane.geometryControlsState = setupPane.geometryState
                        contentPane.state = "EnterDetails"
                    }
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

        DetailsPane {
            id: detailsPane
        }

        states: [
            State {
                name: "PickGeometryType"
            },
            State {
                name: "EnterDetails"

                PropertyChanges { target: setupPane; visible: false }
                PropertyChanges { target: detailsPane; visible: true }
                PropertyChanges { target: contentPane; contentHeight: detailsPane.implicitHeight }
                PropertyChanges { target: contentPane; contentWidth: detailsPane.implicitWidth }
                PropertyChanges { target: detailsPane; focus: true}
                PropertyChanges { target: detailsPane.nameField; focus: true}
            }
        ]
    }

    function resetUnitChecks() {
        ValidUnits.validMeshUnits = false
        ValidUnits.validCylinderUnits = false
        ValidUnits.showCylinderUnitMessage = false
    }

    onClosing: {
        resetUnitChecks()
    }
}
