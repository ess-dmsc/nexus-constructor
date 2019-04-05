import QtQuick.Controls 2.5

Pane {

    contentWidth: moveUpButton.implicitWidth + moveDownButton.implicitWidth + 10 + deleteButton.implicitWidth
    contentHeight: moveUpButton.implicitHeight

    PaddedButton {
        id: moveUpButton
        anchors.top: parent.top
        anchors.left: parent.left
        text: "Move up"
        onClicked: transformModel.change_position(index, index - 1)
    }
    PaddedButton {
        id: moveDownButton
        anchors.top: moveUpButton.top
        anchors.left: moveUpButton.right
        text: "Move down"
        onClicked: transformModel.change_position(index, index + 1)
    }
    PaddedButton {
        id: deleteButton
        anchors.top: moveUpButton.top
        anchors.right: parent.right
        text: "Delete"
        onClicked: transformModel.delete_transform(index)
        buttonEnabled: deletable
        ToolTip.visible: hovered & !deletable
        ToolTip.delay: 400
        ToolTip.text: "Cannot remove a transform that's in use as a transform parent"
    }
}