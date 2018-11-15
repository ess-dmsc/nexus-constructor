import QtQuick 2.11
import QtQuick.Controls 2.4


Pane {
    property string labelText: ""
    property string editorText: ""
    property real editorWidth: 100
    property var validator: null
    id: pane
    padding: 2
    contentHeight: Math.max(label.height, field.height)
    contentWidth: label.width + field.width
    signal editingFinished

    Label {
        id: label
        anchors.verticalCenter: field.verticalCenter
        anchors.left: parent.left
        text: labelText
    }
    TextField {
        id: field
        focus: true
        anchors.top: parent.top
        anchors.left: label.right
        width: editorWidth
        validator: pane.validator

        text: editorText
        onEditingFinished: {
            editorText = text
            pane.editingFinished()
        }
    }
}
