import QtQuick 2.11
import QtQuick.Controls 2.4
import MyValidators 1.0

/*
 * Controls for defining a components transformation to detector space.
 * Should be used in an environment where the following variables exist:
 * - components (InstrumentModel)
 * - transform_parent_index (integer)
 * - index  (integer)
 * - rotate_x   (float)
 * - rotate_y   (float)
 * - rotate_z   (float)
 * - rotate_angle   (float)
 * - translate_x    (float)
 * - translate_y    (float)
 * - translate_z    (float)
 *
 * This can be acomplished by including it in a delegate in a view on an
 * InstrumentModel, or by defining them as properties in the root object
 * of a file in the 'document tree' these controls are included in.
 */

Item {

    property bool autosave: false

    height: relativePicker.height +
            rotateLabel.height +
            xRotField.height +
            angleField.height +
            translateLabel.height +
            xField.height
    width: xRotField.width + yRotField.width + zRotField.width

    Label {
        id: relativeLabel
        anchors.verticalCenter: relativePicker.verticalCenter
        anchors.left: parent.left
        text: "Transform relative to:"
    }
    ComboBox {
        id: relativePicker
        anchors.top: parent.top
        anchors.left: relativeLabel.right
        model: components
        textRole: "name"
        currentIndex: transform_parent_index
        validator: parentValidator
        onActivated: {
            if(acceptableInput){
                transform_parent_index = currentIndex
            } else {
                currentIndex = transform_parent_index
            }
        }
    }

    Label {
        id: rotateLabel
        anchors.top: relativePicker.bottom
        anchors.left: parent.left
        text: "Rotate"
    }

    LabeledTextField {
        id: xRotField
        anchors.top: rotateLabel.bottom
        anchors.left: parent.left
        labelText: "x:"
        editorText: rotate_x
        validator: numberValidator
        onEditingFinished: rotate_x = parseFloat(editorText)
    }
    LabeledTextField {
        id: yRotField
        anchors.top: xRotField.top
        anchors.horizontalCenter: parent.horizontalCenter
        labelText: "y:"
        editorText: rotate_y
        validator: numberValidator
        onEditingFinished: rotate_y = parseFloat(editorText)
    }
    LabeledTextField {
        id: zRotField
        anchors.top: xRotField.top
        anchors.right: parent.right
        labelText: "z:"
        editorText: rotate_z
        validator: numberValidator
        onEditingFinished: rotate_z = parseFloat(editorText)
    }

    LabeledTextField {
        id: angleField
        anchors.top: xRotField.bottom
        anchors.right: zRotField.right
        labelText: "angle (degrees):"
        editorText: rotate_angle
        validator: angleValidator
        onEditingFinished: rotate_angle = parseFloat(editorText)
    }

    Label {
        id: translateLabel
        anchors.top: angleField.bottom
        anchors.left: parent.left
        text: "Translate"
    }

    LabeledTextField {
        id: xField
        anchors.top: translateLabel.bottom
        anchors.left: parent.left
        labelText: "x:"
        editorText: translate_x
        validator: numberValidator
        onEditingFinished: translate_x = parseFloat(editorText)
    }
    LabeledTextField {
        id: yField
        anchors.top: xField.top
        anchors.horizontalCenter: parent.horizontalCenter
        labelText: "y:"
        editorText: translate_y
        validator: numberValidator
        onEditingFinished: translate_y = parseFloat(editorText)
    }
    LabeledTextField {
        id: zField
        anchors.top: xField.top
        anchors.right: parent.right
        labelText: "z:"
        editorText: translate_z
        validator: numberValidator
        onEditingFinished: translate_z = parseFloat(editorText)
    }

    DoubleValidator {
        id: numberValidator
        notation: DoubleValidator.StandardNotation
    }

    DoubleValidator {
        id: angleValidator
        top: 360
        bottom: -360
        notation: DoubleValidator.StandardNotation
    }

    ParentValidator {
        id: parentValidator
        model: components
        myindex: index
        onValidationFailed: {
            relativePicker.ToolTip.show("Items cannot be selected if they would cause a circular dependency", 5000)
        }
    }
}
