import QtQuick 2.11
import QtQuick.Controls 2.4


Pane {
    property alias labelText: label.text
    property alias editorText: field.text
    property alias editorWidth: field.width
    property alias validator: field.validator
    property bool anchoredEditor: false
    property bool selectable: true

    id: pane
    padding: 2
    contentHeight: Math.max(label.height, field.height)
    contentWidth: label.width + (anchoredEditor ? field.implicitWidth : field.width)
    signal editingFinished

    Label {
        id: label
        anchors.verticalCenter: field.verticalCenter
        anchors.left: parent.left
    }
    TextField {
        id: field
        focus: true
        anchors.top: parent.top
        anchors.left: label.right
        anchors.right: anchoredEditor ? parent.right : undefined
        implicitWidth: 100
        onEditingFinished: pane.editingFinished()
        selectByMouse: selectable
    }
}
