import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Dialogs 1.3
import MyModels 1.0
import QtQuick.Layouts 1.11
import MyValidators 1.0
import "."

Pane {
    property var geometryModel

    id: pane
    padding: 0
    contentWidth: view.implicitWidth
    contentHeight: view.height

    signal meshChanged()
    signal cylinderChanged()

    ListView {
        id: view
        height: contentHeight
        anchors.left: parent.left
        anchors.right: parent.right
        interactive: false
    }

    OFFModel {
        id: offModel
        onMeshLoaded: pane.meshChanged()
    }

    CylinderModel {
        id: cylinderModel
        onDataChanged: pane.cylinderChanged()
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
                onEditingFinished: file_url = editorText
            }
            PaddedButton {
                id: chooseFileButton
                anchors.verticalCenter: fileTextField.verticalCenter
                anchors.right: parent.right
                text: "Choose file"
                onClicked: filePicker.open()
            }
            FileDialog {
                id: filePicker
                title: "Choose geometry file"
                nameFilters: ["Geometry files (*.off *.stl *.OFF *.STL)", "Object File Format (*.off *.OFF)", "STL files (*.stl *.STL)"]
                onAccepted: {
                    unitSelection.open()
                    visible: false
                }
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
                        // labelText: "Geometry file:"
                        editorText: units
                        Layout.fillWidth: true
                        anchoredEditor: true
                        onEditingFinished: units = editorText

                        validator: UnitValidator {
                            id: meshUnitValidator
                            onValidationFailed: { ValidUnits.validMeshUnits = false }
                            onValidationSuccess: { ValidUnits.validMeshUnits = true }
                        }
                    }

                    Text {

                        // Blank invalid unit warning - only set if unit validation function returns false
                        id: invalidUnitWarning
                        text: ""
                        color: "red"
                        Layout.fillWidth: true
                        visible: true
                    }

                    RowLayout {

                        Button {
                            id: acceptUnitsButton
                            text: "OK"
                            onClicked: {

                                if (!ValidUnits.validMeshUnits) {
                                    // Invalid units given - Show a message and clear input box
                                    invalidMeshUnitWarning.text = "Units not recognised. Please enter a different type."
                                }
                                else {
                                    // Valid units given - Close the box
                                    file_url = filePicker.fileUrl
                                    unitSelection.close()
                                }

                                // Clear the unit input
                                unitInput.editorText = ""
                            }
                        }

                        Button {
                            id: cancelUnitsButton
                            text: "Cancel"
                            onClicked: {

                                unitSelection.close()
                                // Clear the unit input
                                unitInput.editorText = ""
                            }
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
                contentWidth: Math.max(heightField.implicitWidth + radiusField.implicitWidth + unitsField.implicitWidth,
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
                    // onEditingFinished: cylinder_radius = parseFloat(editorText)
                    validator: UnitValidator {
                                   id: cylinderUnitValidator
                                   onValidationFailed: { ValidUnits.validCylinderUnits = false }
                                   onValidationSuccess: { ValidUnits.validCylinderUnits = true }
                               }
                }

                Text {

                    // Blank invalid unit warning - only set if unit validation function returns false
                    id: invalidCylinderUnitWarning
                    anchors.top: unitsField.bottom
                    text: ValidUnits.cylinderUnitMessage ? "Units not recognised. Please enter a different type." : ""
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
        }
    ]
}
