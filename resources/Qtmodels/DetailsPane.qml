import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0
import QtQuick.Dialogs 1.3

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

    property alias pixelControlsState: pixelControls.state
    property alias geometryControlsState: geometryControls.state
    property alias nameField: nameField

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

            if (setupPane.geometryState == "OFF" && GeometryFileSelected.geometryFileSelected == false)
            {
                noGeometryFileDialog.open()
            }
            // Check that either the mesh or the cylinder were given a valid unit argument because it is not
            // known which geometry has just been created. If the component has no shape, add anyway.
            else if (ValidUnits.validMeshUnits || ValidUnits.validCylinderUnits || setupPane.geometryState == "None") {

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
    MessageDialog {
        id: noGeometryFileDialog
        icon: StandardIcon.Critical
        title: "No Geometry File Given."
        text: "No Geometry file given. Please select a geometry file in order to create a mesh."
        visible: false
    }
}