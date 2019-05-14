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
    implicitWidth: transformColumn.implicitWidth
    implicitHeight: transformColumn.implicitHeight
    property TransformationModel transformModel
    property int componentIndex
    property var transformTextFieldWidth: 90

    ColumnLayout {
        id: transformColumn
        anchors.right: parent.right
        anchors.left: parent.left

        GridLayout {
            id: transformPickerGrid
            rows: 2
            columns: 2

            Label {
                id: relativeLabel
                text: "Transform parent:"
                Layout.fillWidth: false
            }
            ComboBox {
                id: relativePicker
                Layout.preferredWidth: 250
                Layout.fillWidth: true
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
            Item {
                // Spacer Item to force parentTransformPicker to the bottom-right corner of the 4x4 grid
                Layout.preferredWidth: relativeLabel.width
                Layout.fillWidth: false
            }
            ComboBox {
                id: parentTransformPicker
                Layout.preferredWidth: 250
                Layout.fillWidth: true
                model: components.get_transform_model(transform_parent_index)
                textRole: "name"
                currentIndex: dependent_transform_index
                onActivated: dependent_transform_index = currentIndex
            }
        }
        Frame {
            id: transformsListContainer
            // contentWidth: transformsListView.implicitWidth
            contentHeight: transformsListView.implicitHeight
            visible: contentHeight > 0
            padding: 1
            Layout.fillWidth: true

            ListView {
                id: transformsListView
                model: transformModel
                delegate: transformDelegate
                implicitHeight: (contentHeight < 250) ? contentHeight : 250
                anchors.right: parent.right
                anchors.left: parent.left
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ActiveScrollBar {}
            }
        }
        RowLayout {
            id: addTransformationButtonsRow

            PaddedButton {
                id: addTranslate
                text: "Add translation"
                onClicked: transformModel.add_translate()
            }

            PaddedButton {
                id: addRotate
                text: "Add rotation"
                onClicked: transformModel.add_rotate()
            }
            Item {
                // Spacer Item to force Add Transformation buttons to the LHS
                Layout.fillWidth: true
            }
        }
    }

    Component {
        id: transformDelegate

        Frame {
            id: transformBox
            contentHeight: transformBoxColumn.height
            // contentWidth: transformBoxColumn.width
            anchors.right: parent.right
            anchors.left: parent.left

            Component.onCompleted: {
                if (transformsListView.implicitWidth < transformBox.implicitWidth) {
                    transformsListView.implicitWidth = transformBox.implicitWidth
                }
            }

            ColumnLayout {
                id: transformBoxColumn
                anchors.right: parent.right
                anchors.left: parent.left

                StackLayout {
                    id: transformBoxStack
                    currentIndex: transform_type == "Translate" ? 0 : 1
                    Layout.preferredHeight: currentIndex == 0 ? translatePane.implicitHeight : rotatePane.implicitHeight
                    Layout.fillWidth: true

                    Pane {
                        id: translatePane
                        padding: 0
                        contentWidth: translatePaneGrid.implicitWidth
                        contentHeight: translatePaneGrid.implicitHeight
                        Layout.fillWidth: true

                        GridLayout {
                            id: translatePaneGrid
                            rows: 2
                            columns: 6
                            anchors.right: parent.right
                            anchors.left: parent.left

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
                                Layout.minimumWidth: transformTextFieldWidth
                                text: name
                                selectByMouse: true
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
                                Layout.minimumWidth: transformTextFieldWidth
                                text: translate_x
                                selectByMouse: true
                                validator: numberValidator
                                onEditingFinished: translate_x = parseFloat(text)
                            }
                            Label {
                                text: "Y: "
                            }
                            TextField {
                                id: yTranslationField
                                Layout.minimumWidth: transformTextFieldWidth
                                text: translate_y
                                selectByMouse: true
                                validator: numberValidator
                                onEditingFinished: translate_y = parseFloat(text)
                            }
                            Label {
                                text: "Z: "
                            }
                            TextField {
                                id: zTranslationField
                                Layout.minimumWidth: transformTextFieldWidth
                                text: translate_z
                                selectByMouse: true
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
                        Layout.fillWidth: true
                        visible: true

                        GridLayout {
                            id: rotatePaneGrid
                            anchors.right: parent.right
                            anchors.left: parent.left
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
                                selectByMouse: true
                                onEditingFinished: name = text
                                Layout.minimumWidth: transformTextFieldWidth
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
                                Layout.minimumWidth: transformTextFieldWidth
                                text: rotate_x
                                selectByMouse: true
                                validator: numberValidator
                                onEditingFinished: rotate_x = parseFloat(text)
                            }
                            Label {
                                text: "Y: "
                            }
                            TextField {
                                id: yRotationField
                                Layout.minimumWidth: transformTextFieldWidth
                                text: rotate_y
                                selectByMouse: true
                                validator: numberValidator
                                onEditingFinished: rotate_y = parseFloat(text)
                            }
                            Label {
                                text: "Z: "
                            }
                            TextField {
                                id: zRotationField
                                Layout.minimumWidth: transformTextFieldWidth
                                text: rotate_y
                                selectByMouse: true
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
                                Layout.minimumWidth: transformTextFieldWidth
                                text: rotate_angle
                                selectByMouse: true
                                validator: angleValidator
                                onEditingFinished: rotate_angle = parseFloat(text)
                            }
                        }
                    }
                }
                Pane {
                    id: transformButtons
                    contentWidth: transformButtonsRow.implicitWidth
                    contentHeight: transformButtonsRow.implicitHeight
                    Layout.fillWidth: true

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
                            Layout.fillWidth: true
                        }
                        PaddedButton {
                            id: deleteButton
                            text: "Delete"
                            Layout.alignment: Qt.AlignRight
                            onClicked: transformModel.delete_transform(index)
                            buttonEnabled: deletable
                            ToolTip.visible: hovered & !deletable
                            ToolTip.delay: 400
                            ToolTip.text: "Cannot remove a transform that's in use as a transform parent"
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
