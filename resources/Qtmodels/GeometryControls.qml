import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Dialogs 1.3
import MyModels 1.0
import QtQuick.Layouts 1.11
import MyValidators 1.0
import GeometryValidator 1.0

Pane {
    property var geometryModel: noShapeModel

    id: pane
    padding: 0
    contentWidth: view.implicitWidth
    contentHeight: view.height

    signal meshChanged()
    signal cylinderChanged()
    signal noShapeChanged()

    ListView {
        id: view
        height: contentHeight
        anchors.left: parent.left
        anchors.right: parent.right
        interactive: false
    }

    OFFModel {
        id: offModel
        onDataChanged: pane.meshChanged()
    }

    CylinderModel {
        id: cylinderModel
        onDataChanged: pane.cylinderChanged()
    }

    NoShapeModel {
        id: noShapeModel
        onDataChanged: pane.noShapeChanged()
    }

    GeometryValidator {
        id: geometryValidator
    }

    Component {
        id: offDelegate
        Item {
            id: offContainer
            width: view.width
            implicitWidth: fileTextField.implicitWidth + chooseFileButton.width
            height: Math.max(fileTextField.height, chooseFileButton.height)

            Component.onCompleted: view.implicitWidth = offContainer.implicitWidth

            LabeledTextField {
                id: fileTextField
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: chooseFileButton.left
                labelText: "Geometry file:"
                editorText: file_url
                anchoredEditor: true
                readOnly: true
            }
            PaddedButton {
                id: chooseFileButton
                anchors.verticalCenter: fileTextField.verticalCenter
                anchors.right: parent.right
                text: "Choose file"
                onClicked: {
                    filePicker.open()
                }
            }
            FileDialog {
                id: filePicker
                title: "Choose geometry file"
                nameFilters: ["Geometry files (*.off *.stl *.OFF *.STL)", "Object File Format (*.off *.OFF)", "STL files (*.stl *.STL)"]
                onAccepted: {
                    if (geometryValidator.validate_geometry_file(fileUrl)) {
                        // Valid Geometry file given - Accept file and ask user to give the units
                        unitSelection.open()
                        visible: false
                    }
                    else {
                        // Invalid Geometry file given - Reject file
                        reject()
                        invalidGeometryFileDialog.open()
                        GeometryFileSelected.geometryFileSelected = false
                    }
                }
            }
            MessageDialog {
                id: invalidGeometryFileDialog
                icon: StandardIcon.Critical
                title: "Invalid Geometry File"
                text: "Invalid Geometry file given. Please select a different file."
                visible: false
            }
            Dialog {

                id: unitSelection
                title: "Select Units"
                visible: false

                // Remove standard buttons so that custom OK button can be used that only accepts valid units
                standardButtons: StandardButton.NoButton

                // Prevent the window from suddenly expanding when the invalid units message is shown
                width: 350

                ColumnLayout {

                    anchors.fill: parent

                    Text {
                        id: inputText
                        text: "Enter the geometry units: "
                        Layout.fillWidth: true
                    }

                    LabeledTextField {
                        id: unitInput
                        editorText: units
                        Layout.fillWidth: true
                        anchoredEditor: true

                        validator: UnitValidator {
                            id: meshUnitValidator
                            onValidationFailed: {
                                acceptUnitsButton.enabled = false
                                invalidMeshUnitWarning.visible = true
                            }
                            onValidationSuccess: {
                                acceptUnitsButton.enabled = true
                                invalidMeshUnitWarning.visible = false
                            }
                        }
                    }

                    Text {

                        // Blank invalid unit warning - only set if unit validation function returns false
                        id: invalidMeshUnitWarning
                        text: ValidUnits.invalidUnitsText
                        color: "red"
                        Layout.fillWidth: true
                        visible: false
                    }

                    RowLayout {

                        Button {
                            id: acceptUnitsButton
                            text: "OK"
                            onClicked: {
                                // Close the box
                                offModel.file_url = filePicker.fileUrl
                                offModel.units = unitInput.editorText
                                GeometryFileSelected.geometryFileSelected = true
                                unitSelection.close()
                            }
                        }

                        Button {
                            id: cancelUnitsButton
                            text: "Cancel"
                            onClicked: unitSelection.close()
                        }
                    }
                }
            }
        }
    }

    Component {
        id: cylinderDelegate
        Item {
            id: cylinderContainer
            width: view.width
            implicitWidth: fields.implicitWidth
            height: cylinderLabel.height + fields.height

            Component.onCompleted: view.implicitWidth = cylinderContainer.implicitWidth

            Label {
                id: cylinderLabel
                anchors.top: parent.top
                anchors.left: parent.left
                text: "Cylinder Geometry:"
            }

            Frame {
                id: fields
                anchors.top: cylinderLabel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                contentWidth: Math.max(heightField.implicitWidth + radiusField.implicitWidth + unitsField.implicitWidth + invalidUnitCross.implicitWidth,
                                       axisXField.implicitWidth + axisYField.implicitWidth + axisZField.implicitWidth)
                contentHeight: heightField.implicitHeight + directionLabel.implicitHeight + axisXField.implicitHeight
                               + invalidCylinderUnitWarning.implicitHeight

                LabeledTextField {
                    id: heightField
                    anchors.top: parent.top
                    anchors.left: parent.left
                    labelText: "height:"
                    editorText: cylinder_height
                    onEditingFinished: cylinder_height = parseFloat(editorText)
                    validator: numberValidator
                }
                LabeledTextField {
                    id: radiusField
                    anchors.top: heightField.top
                    anchors.left: heightField.right
                    labelText: "radius:"
                    editorText: cylinder_radius
                    onEditingFinished: cylinder_radius = parseFloat(editorText)
                    validator: numberValidator
                }

                LabeledTextField {
                    id: unitsField
                    anchors.top: heightField.top
                    anchors.left: radiusField.right
                    labelText: "Units:"
                    editorText: cylinder_units
                    onEditingFinished: cylinder_units = editorText
                    validator: UnitValidator {
                                    id: cylinderUnitValidator
                                    onValidationFailed: { ValidUnits.validCylinderUnits = false }
                                    onValidationSuccess: { ValidUnits.validCylinderUnits = true }
                               }
                }
                Text {
                    id: invalidUnitCross
                    anchors.left: unitsField.right
                    anchors.right: parent.right
                    text: "❌"
                    color: "red"
                    font.pointSize: 18
                    visible: !ValidUnits.validCylinderUnits

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        ToolTip.visible: invalidUnitCross.visible && containsMouse
                        ToolTip.text: ValidUnits.invalidUnitsText
                    }
                }

                Text {

                    // Blank invalid unit warning - only set to contain text if unit validation function returns false
                    // and user presses "Add" button
                    id: invalidCylinderUnitWarning
                    anchors.top: unitsField.bottom
                    text: ValidUnits.showCylinderUnitMessage ? ValidUnits.invalidUnitsText : ""
                    color: "red"
                    Layout.fillWidth: true
                    visible: true
                 }

                Label {
                    id: directionLabel
                    anchors.top: invalidCylinderUnitWarning.bottom
                    anchors.left: parent.left
                    text: "axis direction:"
                }

                LabeledTextField {
                    id: axisXField
                    anchors.top: directionLabel.bottom
                    anchors.left: parent.left
                    labelText: "x:"
                    editorText: axis_x
                    onEditingFinished: axis_x = parseFloat(editorText)
                    validator: numberValidator
                }
                LabeledTextField {
                    id: axisYField
                    anchors.top: axisXField.top
                    anchors.horizontalCenter: parent.horizontalCenter
                    labelText: "y:"
                    editorText: axis_y
                    onEditingFinished: axis_y = parseFloat(editorText)
                    validator: numberValidator
                }
                LabeledTextField {
                    id: axisZField
                    anchors.top: axisXField.top
                    anchors.right: parent.right
                    labelText: "z:"
                    editorText: axis_z
                    onEditingFinished: axis_z = parseFloat(editorText)
                    validator: numberValidator
                }
            }
        }
    }

    DoubleValidator {
        id: numberValidator
        notation: DoubleValidator.StandardNotation
    }


    states: [
        State {
            name: "OFF"
            PropertyChanges { target: pane; geometryModel: offModel }

            PropertyChanges { target: view; model: offModel}
            PropertyChanges { target: view; delegate: offDelegate}
        },
        State {
            name: "Cylinder"
            PropertyChanges { target: pane; geometryModel: cylinderModel }

            PropertyChanges { target: view; model: cylinderModel}
            PropertyChanges { target: view; delegate: cylinderDelegate}
        },
        State {
            name: "None"
            PropertyChanges { target: pane; geometryModel: noShapeModel }
            PropertyChanges { target: view; model: noShapeModel }
        }
    ]
}
