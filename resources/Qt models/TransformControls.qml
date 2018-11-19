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

    function saveFields(){
        saveParentIndex()
        saveRotateX()
        saveRotateY()
        saveRotateZ()
        saveRotateAngle()
        saveTranslateX()
        saveTranslateY()
        saveTranslateZ()
    }
    function resetFields(){
        relativePicker.currentIndex = transform_parent_index
        xRotField.editorText = rotate_x
        yRotField.editorText = rotate_y
        zRotField.editorText = rotate_z
        angleField.editorText = rotate_angle
        xField.editorText = translate_x
        yField.editorText = translate_y
        zField.editorText = translate_z
    }

    function saveParentIndex(){
        transform_parent_index = relativePicker.currentIndex
    }
    function saveRotateX(){
        rotate_x = parseFloat(xRotField.editorText)
    }
    function saveRotateY(){
        rotate_y = parseFloat(yRotField.editorText)
    }
    function saveRotateZ(){
        rotate_z = parseFloat(zRotField.editorText)
    }
    function saveRotateAngle(){
        rotate_angle = parseFloat(angleField.editorText)
    }
    function saveTranslateX(){
        translate_x = parseFloat(xField.editorText)
    }
    function saveTranslateY(){
        translate_y = parseFloat(yField.editorText)
    }
    function saveTranslateZ(){
        translate_z = parseFloat(zField.editorText)
    }

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
            if(!acceptableInput){
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
        onEditingFinished: if (autosave){
            saveRotateX()
        }
    }
    LabeledTextField {
        id: yRotField
        anchors.top: xRotField.top
        anchors.horizontalCenter: parent.horizontalCenter
        labelText: "y:"
        editorText: rotate_y
        validator: numberValidator
        onEditingFinished: if (autosave){
            saveRotateY()
        }
    }
    LabeledTextField {
        id: zRotField
        anchors.top: xRotField.top
        anchors.right: parent.right
        labelText: "z:"
        editorText: rotate_z
        validator: numberValidator
        onEditingFinished: if (autosave){
            saveRotateZ()
        }
    }

    LabeledTextField {
        id: angleField
        anchors.top: xRotField.bottom
        anchors.right: zRotField.right
        labelText: "angle (degrees):"
        editorText: rotate_angle
        validator: angleValidator
        onEditingFinished: if (autosave){
            saveRotateAngle()
        }
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
        onEditingFinished: if (autosave){
            saveTranslateX()
        }
    }
    LabeledTextField {
        id: yField
        anchors.top: xField.top
        anchors.horizontalCenter: parent.horizontalCenter
        labelText: "y:"
        editorText: translate_y
        validator: numberValidator
        onEditingFinished: if (autosave){
            saveTranslateY()
        }
    }
    LabeledTextField {
        id: zField
        anchors.top: xField.top
        anchors.right: parent.right
        labelText: "z:"
        editorText: translate_z
        validator: numberValidator
        onEditingFinished: if (autosave){
            saveTranslateZ()
        }
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
