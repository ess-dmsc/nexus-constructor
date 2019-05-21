import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Dialogs 1.3
import MyModels 1.0
import QtQuick.Layouts 1.11
import MyValidators 1.0
import GeometryValidator 1.0

Pane {
    property var geometryModel: noShapeModel
    property var textFieldWidth: 100

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
            implicitWidth: geometryFileRow.implicitWidth
            height: geometryFileRow.implicitHeight

            Component.onCompleted: view.implicitWidth = offContainer.implicitWidth

            RowLayout {
                id: geometryFileRow
                anchors.right: parent.right
                anchors.left: parent.left

                Text {
                    text: "Geometry File: "
                }
                TextField {
                    id: fileTextField
                    text: file_url
                    readOnly: true
                    Layout.fillWidth: true
                }
                PaddedButton {
                    id: chooseFileButton
                    text: "Choose file"
                    onClicked: {
                        filePicker.open()
                    }
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

                ColumnLayout {
                    anchors.fill: parent

                    Text {
                        id: inputText
                        text: "Enter the geometry units: "
                        Layout.fillWidth: true
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.minimumWidth: 350
                        LabeledTextField {
                            id: unitInput
                            editorText: units
                            Layout.fillWidth: true
                            anchoredEditor: true

                            validator: UnitValidator {
                                id: meshUnitValidator
                                onValidationFailed: {
                                    acceptUnitsButton.enabled = false
                                    invalidMeshUnitsCross.visible = true
                                }
                                onValidationSuccess: {
                                    acceptUnitsButton.enabled = true
                                    invalidMeshUnitsCross.visible = false
                                }
                            }
                        }
                        InvalidInputCross {
                            id: invalidMeshUnitsCross
                            toolTipMessage: ErrorMessages.invalidUnits
                        }
                    }
                    RowLayout {

                        Button {
                            id: acceptUnitsButton
                            text: "OK"
                            onClicked: {
                                // Close the box
                                // Must set units before the file_url as units are converted when file is loaded
                                offModel.units = unitInput.editorText
                                offModel.file_url = filePicker.fileUrl
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
            implicitWidth: cylinderColumn.implicitWidth
            height: cylinderColumn.implicitHeight

            Component.onCompleted: view.implicitWidth = cylinderContainer.implicitWidth

            ColumnLayout {
                id: cylinderColumn
                anchors.fill: parent

                Label {
                    id: cylinderLabel
                    text: "Cylinder Geometry:"
                }

                Frame {
                    id: fields
                    Layout.fillWidth: true

                    GridLayout {
                        id: cylinderFieldGrid
                        columns: 7
                        rows: 3
                        anchors.right: parent.right
                        anchors.left: parent.left

                        Label {
                            text: "Height: "
                            Layout.alignment: Qt.AlignRight
                        }
                        TextField {
                            id: heightField
                            text: cylinder_height
                            onEditingFinished: cylinder_height = parseFloat(text)
                            validator: numberValidator
                            Layout.preferredWidth: textFieldWidth
                            Layout.fillWidth: true
                        }
                        Label {
                            text: "Radius: "
                            Layout.alignment: Qt.AlignRight
                        }
                        TextField {
                            id: radiusField
                            text: cylinder_radius
                            onEditingFinished: cylinder_radius = parseFloat(text)
                            validator: numberValidator
                            Layout.preferredWidth: textFieldWidth
                            Layout.fillWidth: true
                        }
                        Label {
                            text: "Units: "
                            Layout.alignment: Qt.AlignRight
                        }
                        TextField {
                            id: unitsField
                            text: cylinder_units
                            onEditingFinished: cylinder_units = text
                            validator: UnitValidator {
                                           id: cylinderUnitValidator
                                           onValidationFailed: { ValidUnits.validCylinderUnits = false }
                                           onValidationSuccess: { ValidUnits.validCylinderUnits = true }
                                       }
                            Layout.preferredWidth: textFieldWidth
                            Layout.fillWidth: true
                        }
                        InvalidInputCross {
                            id: invalidCylinderUnitsCross
                            opacity: !ValidUnits.validCylinderUnits
                            toolTipMessage: ErrorMessages.invalidUnits
                            Layout.fillWidth: false
                        }
                        Label {
                            text: "Axis Direction:"
                            Layout.columnSpan: 7
                            Layout.fillWidth: true
                        }
                        Label {
                            text: "X:"
                            Layout.alignment: Qt.AlignRight
                        }
                        TextField {
                            id: axisXField
                            text: axis_x
                            onEditingFinished: axis_x = parseFloat(text)
                            validator: numberValidator
                            Layout.preferredWidth: textFieldWidth
                            Layout.fillWidth: true
                        }
                        Label {
                            text: "Y:"
                            Layout.alignment: Qt.AlignRight
                        }
                        TextField {
                            id: axisYField
                            text: axis_y
                            onEditingFinished: axis_y = parseFloat(text)
                            validator: numberValidator
                            Layout.preferredWidth: textFieldWidth
                            Layout.fillWidth: true
                        }
                        Label {
                            text: "Z: "
                            Layout.alignment: Qt.AlignRight
                        }
                        TextField {
                            id: axisZField
                            text: axis_z
                            onEditingFinished: axis_z = parseFloat(text)
                            validator: numberValidator
                            Layout.preferredWidth: textFieldWidth
                            Layout.fillWidth: true
                        }
                        Item {
                            // Spacer item to fill the remaining part of the grid
                            Layout.preferredWidth: invalidCylinderUnitsCross.width
                            Layout.fillWidth: false
                        }
                    }
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
