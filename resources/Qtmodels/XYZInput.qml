import QtQuick.Layouts 1.11
import MyValidators 1.0
import QtQuick 2.11
// import QtQuick.Controls 2.4

RowLayout {

    id: root

    property alias xEditorText: xField.editorText
    property alias yEditorText: yField.editorText
    property alias zEditorText: zField.editorText

    signal xEditingFinished()
    signal yEditingFinished()
    signal zEditingFinished()

    LabeledTextField {
        id: xField
        labelText: "x: "
        // editorText: translate_x
        validator: numberValidator
        // onEditingFinished: translate_x = parseFloat(editorText)
        onEditingFinished: root.xEditingFinished()
    }
    LabeledTextField {
        id: yField
        labelText: "y: "
        // editorText: translate_y
        validator: numberValidator
        // onEditingFinished: translate_y = parseFloat(editorText)
        onEditingFinished: root.yEditingFinished()
    }
    LabeledTextField {
        id: zField
        labelText: "z: "
        // editorText: translate_z
        validator: numberValidator
        // onEditingFinished: translate_z = parseFloat(editorText)
        onEditingFinished: root.zEditingFinished()
    }
    DoubleValidator {
        id: numberValidator
        notation: DoubleValidator.StandardNotation
    }

}
