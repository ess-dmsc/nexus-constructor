import QtQuick 2.11
import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0

/*
 * Controls for defining a components transformation to detector space.
 * Should be used in an environment where the following variables exist:
 * - components (InstrumentModel)
 * - transform_parent_index (integer)
 * - index  (integer)
 *
 * This can be acomplished by including it in a delegate in a view on an
 * InstrumentModel, or by defining them as properties in the root object
 * of a file in the 'document tree' these controls are included in.
 */

Item {
    id: transformsItem

    height: relativePicker.height +
            transformsListView.height +
            addTranslate.height
    implicitWidth: Math.max(relativeLabel.implicitWidth + relativePicker.implicitWidth,
                            transformsListView.implicitWidth,
                            addTranslate.implicitWidth + addRotate.implicitWidth)
    property TransformationModel model: transformModel

    signal transformsChanged()

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

    ListView {
        id: transformsListView
        anchors.top: relativePicker.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        model: transformModel
        delegate: transformDelegate
        height: contentHeight
        clip: true
    }

    PaddedButton {
        id: addTranslate
        anchors.top: transformsListView.bottom
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

    TransformationModel {
        id: transformModel
        onTransformsUpdated: transformsItem.transformsChanged()
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
                contentWidth: xField.implicitWidth + yField.implicitWidth + zField.implicitWidth
                contentHeight: translateNameField.height + xField.height

                Label {
                    id: translateLabel
                    anchors.verticalCenter: translateNameField.verticalCenter
                    anchors.left: parent.left
                    text: "Translation"
                }
                LabeledTextField {
                    id: translateNameField
                    anchors.top: parent.top
                    anchors.right: parent.right
                    labelText: "Name:"
                    editorText: name
                }

                LabeledTextField {
                    id: xField
                    anchors.top: translateNameField.bottom
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
            }

            Pane {
                id: rotatePane
                padding: 0
                contentWidth: xRotField.implicitWidth + yRotField.implicitWidth + zRotField.implicitWidth
                contentHeight: rotateNameField.height + xRotField.height + angleField.height

                Label {
                    id: rotateLabel
                    anchors.verticalCenter: rotateNameField.verticalCenter
                    anchors.left: parent.left
                    text: "Rotation"
                }
                LabeledTextField {
                    id: rotateNameField
                    anchors.top: parent.top
                    anchors.right: parent.right
                    labelText: "Name:"
                    editorText: name
                }

                LabeledTextField {
                    id: xRotField
                    anchors.top: rotateNameField.bottom
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
            }

            Pane {
                id: transformButtons
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
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
        myindex: index
        onValidationFailed: {
            relativePicker.ToolTip.show("Items cannot be selected if they would cause a circular dependency", 5000)
        }
    }
}
