import QtQuick 2.11
import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0

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
            contentHeight: typeLabel.height +
                           typePane.height +
                           geometryLabel.height +
                           geometryPane.height +
                           pixelLabel.height +
                           pixelPane.height +
                           continueButton.height
            contentWidth: Math.max(typeLabel.width,
                                   typePane.width,
                                   geometryLabel.width,
                                   geometryPane.width,
                                   pixelLabel.width,
                                   pixelPane.width,
                                   250)

            property var selectedType
            property string geometryState
            property string pixelState

            Label {
                id: typeLabel
                anchors.left: parent.left
                anchors.top: parent.top
                text: "Component type:"
            }

            Pane {
                id: typePane
                anchors.top: typeLabel.bottom
                anchors.left: parent.left

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
                anchors.left: parent.left
                anchors.top: typePane.bottom
                text: "Geometry:"
            }
            Pane {
                id: geometryPane
                anchors.left: parent.left
                anchors.top: geometryLabel.bottom
                contentWidth: meshRadio.width + cylinderRadio.width
                contentHeight: Math.max(meshRadio.height, cylinderRadio.height)

                RadioButton {
                    id: meshRadio
                    anchors.left: parent.left
                    anchors.top: parent.top
                    text: "Mesh"
                    onClicked: setupPane.geometryState = "OFF"

                    checked: true
                    Component.onCompleted: setupPane.geometryState = "OFF"
                }
                RadioButton {
                    id: cylinderRadio
                    anchors.left: meshRadio.right
                    anchors.top: meshRadio.top
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
                    anchors.left: cylinderRadio.right
                    anchors.top: cylinderRadio.top
                    text: "None"
                    onClicked: setupPane.geometryState = "None", setupPane.pixelState = ""
                }
            }

            Label {
                id: pixelLabel
                anchors.left: parent.left
                anchors.top: geometryPane.bottom
                text: "Pixels:"
                enabled: !noShapeRadio.checked
            }
            Pane {
                id: pixelPane
                anchors.left: parent.left
                anchors.top: pixelLabel.bottom
                contentWidth: Math.max(singlePixelRadio.width,
                                       pixelGridRadio.width,
                                       mappedMeshRadio.width,
                                       noPixelRadio.width)
                contentHeight:singlePixelRadio.height +
                              pixelGridRadio.height +
                              mappedMeshRadio.height +
                              noPixelRadio.height
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

                RadioButton {
                    id: singlePixelRadio
                    anchors.top: parent.top
                    text: "Single ID"
                    enabled: setupPane.selectedType.allowSingleID
                    onCheckedChanged: if (checked) setupPane.pixelState = "SinglePixel"
                }
                RadioButton {
                    id: pixelGridRadio
                    anchors.top: singlePixelRadio.bottom
                    text: "Repeatable grid"
                    enabled: setupPane.selectedType.allowPixelGrid
                    onCheckedChanged: if (checked) setupPane.pixelState = "Grid"
                }
                RadioButton {
                    id: mappedMeshRadio
                    anchors.top: pixelGridRadio.bottom
                    text: "Face mapped mesh"
                    enabled: setupPane.selectedType.allowMappedMesh && meshRadio.checked
                    onCheckedChanged: if (checked) setupPane.pixelState = "Mapping"
                }
                RadioButton {
                    id: noPixelRadio
                    anchors.top: mappedMeshRadio.bottom
                    text: "None"
                    enabled: setupPane.selectedType.allowNoPixels
                    onCheckedChanged: if (checked) setupPane.pixelState = ""
                }
            }

            PaddedButton {
                id: continueButton
                anchors.top: pixelPane.bottom
                anchors.left: parent.left
                text: "Continue"
                onClicked: {
                    componentType = setupPane.selectedType.name
                    pixelControls.state = setupPane.pixelState
                    geometryControls.state = setupPane.geometryState
                    contentPane.state = "EnterDetails"
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

        Pane {
            id: detailsPane
            contentWidth:  Math.max(transformFrame.implicitWidth, geometryControls.implicitWidth, pixelControls.implicitWidth)
            contentHeight: nameField.implicitHeight
                           + descriptionField.implicitHeight
                           + transformLabel.implicitHeight
                           + transformFrame.implicitHeight
                           + geometryControls.implicitHeight
                           + pixelControls.implicitHeight
                           + addButton.implicitHeight
            anchors.fill: parent
            visible: false

            LabeledTextField {
                id: nameField
                labelText: "Name:"
                editorWidth: 200
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
                anchors.bottom: geometryControls.top
                contentHeight: transformControls.implicitHeight
                contentWidth: transformControls.implicitWidth
                anchors.left: parent.left
                anchors.right: parent.right
                TransformControls {
                    id: transformControls
                    transformModel: TransformationModel {}
                    componentIndex: index
                    anchors.fill: parent
                }
            }

            GeometryControls {
                id: geometryControls
                anchors.bottom: pixelControls.top
                anchors.right:parent.right
                anchors.left: parent.left
                onMeshChanged: pixelControls.restartMapping(geometryControls.geometryModel)
            }

            PixelControls {
                id: pixelControls
                anchors.bottom: addButton.top
                anchors.right:parent.right
                anchors.left: parent.left
                visible: state != ""
            }

            PaddedButton {
                id: addButton
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                leftPadding: 0
                text: "Add"
                onClicked: {

                    // Check that either the mesh or the cylinder were given a valid unit argument because it is not
                    // known which geometry has just been created. If the component has no shape, add anyway.
                    if (ValidUnits.validMeshUnits || ValidUnits.validCylinderUnits || setupPane.geometryState == "None") {

                        components.add_component(componentType, name, description, transform_parent_index, dependent_transform_index,
                                                 geometryControls.geometryModel,
                                                 pixelControls.pixelModel,
                                                 transformControls.transformModel)

                        addComponentWindow.close()

                        // Reset the booleans for input validity
                        resetUnitChecks()

                    }
                    else {

                        // Bad units given - Show the bad unit message without creating the geometry
                        ValidUnits.showCylinderUnitMessage = true
                    }

                }
            }
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
                PropertyChanges { target: nameField; focus: true}
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
