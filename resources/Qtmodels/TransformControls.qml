import QtQuick 2.11
import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0
import QtQuick.Layouts 1.11

/*
 * Controls for defining a components transformation to detector space.
 * Should be used in an environment where the following variables exist:
 * - components (InstrumentModel)
 * - transform_parent_index (integer)
 * - dependent_transform_index (integer)
 * - index  (integer)
 *
 * This can be accomplished by including it in a delegate in a view on an
 * InstrumentModel, or by defining them as properties in the root object
 * of a file in the 'document tree' these controls are included in.
 */

Item {
    id: transformsItem

    implicitHeight: relativePicker.implicitHeight +
                    parentTransformPicker.implicitHeight +
                    transformsListContainer.implicitHeight +
                    addTranslate.implicitHeight
    implicitWidth: Math.max(relativeLabel.implicitWidth + relativePicker.implicitWidth,
                            transformsListContainer.implicitWidth,
                            addTranslate.implicitWidth + addRotate.implicitWidth)
    property TransformationModel transformModel
    property int componentIndex
    property var transformTextFieldWidth: 90

    Label {
        id: relativeLabel
        anchors.verticalCenter: relativePicker.verticalCenter
        anchors.left: parent.left
        text: "Transform parent:"
    }
    ComboBox {
        id: relativePicker
        anchors.top: parent.top
        anchors.left: relativeLabel.right
        anchors.right: parent.right
        implicitWidth: 250
        // As the sample is its own transform parent, use an unfiltered model for it to prevent validation errors
        model: (componentIndex == 0) ? components : filteredModel
        textRole: "name"
        currentIndex: (componentIndex == 0) ? transform_parent_index : model.filtered_index(transform_parent_index)
        validator: parentValidator
        onActivated: {
            if(acceptableInput){
                transform_parent_index = model.source_index(currentIndex)
            } else {
                currentIndex = (componentIndex == 0) ? transform_parent_index : model.filtered_index(transform_parent_index)
            }
        }
    }
    ExcludedComponentModel {
        id: filteredModel
        model: components
        index: componentIndex
    }
    ComboBox {
        id: parentTransformPicker
        anchors.top: relativePicker.bottom
        anchors.left: relativePicker.left
        anchors.right: relativePicker.right
        model: components.get_transform_model(transform_parent_index)
        textRole: "name"
        currentIndex: dependent_transform_index
        onActivated: dependent_transform_index = currentIndex
    }

    Frame {
        id: transformsListContainer
        anchors.top: parentTransformPicker.bottom
        anchors.bottom: addTranslate.top
        anchors.left: parent.left
        anchors.right: parent.right
        contentWidth: transformsListView.implicitWidth
        contentHeight: transformsListView.implicitHeight
        visible: contentHeight > 0
        padding: 1

        ListView {
            id: transformsListView
            anchors.fill: parent
            model: transformModel
            delegate: transformDelegate
            implicitHeight: (contentHeight < 250) ? contentHeight : 250
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: ActiveScrollBar {}
        }
    }

    PaddedButton {
        id: addTranslate
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        text: "Add translation"
        onClicked: transformModel.add_translate()
    }

    PaddedButton {
        id: addRotate
        anchors.top: addTranslate.top
        anchors.left: addTranslate.right
        text: "Add rotation"
        onClicked: transformModel.add_rotate()
    }

    Component {
        id: transformDelegate

        Frame {
            id: transformBox
            width: transformsListView.width
            contentHeight: translatePane.height + rotatePane.height + transformButtons.height
            contentWidth: Math.max(translatePane.implicitWidth, rotatePane.implicitWidth, transformButtons.implicitWidth)

            Component.onCompleted: {
                if (transformsListView.implicitWidth < transformBox.implicitWidth) {
                    transformsListView.implicitWidth = transformBox.implicitWidth
                }
            }

            Pane {
                id: translatePane
                padding: 0
                contentWidth: translatePaneGrid.implicitWidth
                contentHeight: translatePaneGrid.implicitHeight

                GridLayout {
                    id: translatePaneGrid
                    rows: 2
                    columns: 6

                    Label {
                        id: translateLabel
                        text: "Translation"
                        Layout.columnSpan: 2
                    }
                    Label {
                        id: translateNameLabel
                        text: "Name: "
                        Layout.columnSpan: 3
                        Layout.alignment: Qt.AlignRight
                    }
                    TextField {
                        id: translateNameField
                        implicitWidth: transformTextFieldWidth
                        text: name
                        onEditingFinished: name = text
                        validator: NameValidator {
                            model: transformModel
                            myindex: index
                            onValidationFailed: translateNameField.ToolTip.show("A component's transforms must have unique names", 3000)
                        }
                    }
                    Label {
                        text: "X: "
                    }
                    TextField {
                        id: xTranslationField
                        implicitWidth: transformTextFieldWidth
                        text: translate_x
                        validator: numberValidator
                        onEditingFinished: translate_x = parseFloat(text)
                    }
                    Label {
                        text: "Y: "
                    }
                    TextField {
                        id: yTranslationField
                        implicitWidth: transformTextFieldWidth
                        text: translate_y
                        validator: numberValidator
                        onEditingFinished: translate_y = parseFloat(text)
                    }
                    Label {
                        text: "Z: "
                    }
                    TextField {
                        id: zTranslationField
                        implicitWidth: transformTextFieldWidth
                        text: translate_z
                        validator: numberValidator
                        onEditingFinished: translate_z = parseFloat(text)
                    }
                }
            }

            Pane {
                id: rotatePane
                padding: 0
                contentWidth: rotatePaneGrid.implicitWidth
                contentHeight: rotatePaneGrid.implicitHeight

                GridLayout {
                    id: rotatePaneGrid
                    anchors.fill: parent
                    rows: 3
                    columns: 6

                    Label {
                        id: rotateLabel
                        text: "Rotation"
                        Layout.columnSpan: 2
                    }
                    Label {
                        id: rotateNameLabel
                        text: "Name: "
                        Layout.alignment: Qt.AlignRight
                        Layout.columnSpan: 3
                    }
                    TextField {
                        id: rotateNameField
                        text: name
                        onEditingFinished: name = text
                        implicitWidth: transformTextFieldWidth
                        validator: NameValidator {
                            model: transformModel
                            myindex: index
                            onValidationFailed: translateNameField.ToolTip.show("A component's transforms must have unique names", 3000)
                        }
                    }
                    Label {
                        text: "X: "
                    }
                    TextField {
                        id: xRotationField
                        implicitWidth: transformTextFieldWidth
                        text: rotate_x
                        validator: numberValidator
                        onEditingFinished: rotate_x = parseFloat(text)
                    }
                    Label {
                        text: "Y: "
                    }
                    TextField {
                        id: yRotationField
                        implicitWidth: transformTextFieldWidth
                        text: rotate_y
                        validator: numberValidator
                        onEditingFinished: rotate_y = parseFloat(text)
                    }
                    Label {
                        text: "Z: "
                    }
                    TextField {
                        id: zRotationField
                        implicitWidth: transformTextFieldWidth
                        text: rotate_y
                        validator: numberValidator
                        onEditingFinished: rotate_y = parseFloat(text)
                    }
                    Label {
                        text: "Angle (Degrees): "
                        Layout.alignment: Qt.AlignRight
                        Layout.columnSpan: 5
                    }
                    TextField {
                        id: angleField
                        implicitWidth: transformTextFieldWidth
                        text: rotate_angle
                        validator: angleValidator
                        onEditingFinished: rotate_angle = parseFloat(text)
                    }
                }
            }

            Pane {
                id: transformButtons
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                contentWidth: transformButtonsRow.implicitWidth
                contentHeight: transformButtonsRow.implicitHeight

                RowLayout {
                    id: transformButtonsRow
                    anchors.fill: parent

                    PaddedButton {
                        id: moveUpButton
                        Layout.fillWidth: false
                        text: "Move up"
                        onClicked: transformModel.change_position(index, index - 1)
                    }
                    PaddedButton {
                        id: moveDownButton
                        Layout.fillWidth: false
                        text: "Move down"
                        onClicked: transformModel.change_position(index, index + 1)
                    }
                    Item {
                        // Spacer item to force deleteButton to the right
                        Layout.fillWidth: true
                    }
                    PaddedButton {
                        id: deleteButton
                        Layout.fillWidth: false
                        text: "Delete"
                        onClicked: transformModel.delete_transform(index)
                        buttonEnabled: deletable
                        ToolTip.visible: hovered & !deletable
                        ToolTip.delay: 400
                        ToolTip.text: "Cannot remove a transform that's in use as a transform parent"
                    }
                }
            }

            states: [
                State {
                    name: "Translate"; when: transform_type == "Translate"
                    PropertyChanges { target: rotatePane; visible: false }
                    PropertyChanges { target: rotatePane; height: 0 }
                },
                State {
                    name: "Rotate"; when: transform_type == "Rotate"
                    PropertyChanges { target: translatePane; visible: false }
                    PropertyChanges { target: translatePane; height: 0 }
                }
            ]
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
        myindex: componentIndex
        onValidationFailed: {
            relativePicker.ToolTip.show("Items cannot be selected if they would cause a circular dependency", 5000)
        }
    }
}
