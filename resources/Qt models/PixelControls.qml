import QtQuick 2.11
import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0

Item {
    property var pixelModel

    id: pane
    height: pixelLabel.height + viewFrame.height

    signal layoutChanged()

    function restartMapping(geometryModel){
        onGeometryModelChanged: mappingModel.restart_mapping(geometryModel)
    }

    Label {
        id: pixelLabel
        anchors.top: parent.top
        anchors.left: parent.left
    }

    Frame {
        id: viewFrame
        anchors.top: pixelLabel.bottom
        contentHeight: view.height
        width: parent.width
        padding: 1
        ListView {
            id: view
            height: contentHeight
            width: parent.width
            interactive: false
            clip: true
        }
    }

    PixelGridModel {
        id: gridModel
        onDataChanged: pane.layoutChanged()
    }

    PixelMappingModel {
        id: mappingModel
    }

    Component {
        id: gridDelegate

        Pane {
            id: gridFields
            contentHeight: rowsField.height +
                columnsField.height +
                firstIdField.height +
                cornerPicker.height +
                directionPicker.height
            width: view.width

            LabeledTextField {
                id: rowsField
                anchors.top: parent.top
                anchors.right: columnsField.right
                labelText: "Rows:"
                editorText: rows
                onEditingFinished: rows = parseInt(editorText)
                validator: integerValidator
            }
            LabeledTextField {
                id: rowHeightField
                anchors.top: rowsField.top
                anchors.right: columnWidthField.right
                labelText: "Row height:"
                editorText: row_height
                onEditingFinished: row_height = parseFloat(editorText)
                validator: numberValidator
            }

            LabeledTextField {
                id: columnsField
                anchors.top: rowHeightField.bottom
                anchors.left: parent.left
                labelText: "Columns:"
                editorText: columns
                onEditingFinished: columns = parseInt(editorText)
                validator: integerValidator
            }
            LabeledTextField {
                id: columnWidthField
                anchors.top: columnsField.top
                anchors.left: columnsField.right
                labelText: "Column width:"
                editorText: col_width
                onEditingFinished: col_width = parseFloat(editorText)
                validator: numberValidator
            }

            LabeledTextField {
                id: firstIdField
                anchors.top: columnWidthField.bottom
                anchors.right: columnsField.right
                labelText: "First ID:"
                editorText: first_id
                onEditingFinished: first_id = parseInt(editorText)
                validator: integerValidator
            }

            Label {
                id: cornerLabel
                anchors.verticalCenter: cornerPicker.verticalCenter
                anchors.left: parent.left
                text: "Start counting ID's from:"
            }
            ComboBox {
                id: cornerPicker
                anchors.top: firstIdField.bottom
                anchors.left: cornerLabel.right
                textRole: "key"
                model: ListModel {
                    ListElement { key: "Bottom left"; value: "BOTTOM_LEFT" }
                    ListElement { key: "Bottom right"; value: "BOTTOM_RIGHT" }
                    ListElement { key: "Top left"; value: "TOP_LEFT" }
                    ListElement { key: "Top right"; value: "TOP_RIGHT" }
                }
                onActivated: initial_count_corner = model.get(currentIndex).value
            }

            Label {
                id: directionLabel
                anchors.verticalCenter: directionPicker.verticalCenter
                anchors.right: cornerLabel.right
                text: "Count first along:"
            }
            ComboBox {
                id: directionPicker
                anchors.top: cornerPicker.bottom
                anchors.left: cornerPicker.left
                textRole: "key"
                model: ListModel {
                    ListElement { key: "Rows"; value: "ROW" }
                    ListElement { key: "Columns"; value: "COLUMN" }
                }
                onActivated: count_direction = model.get(currentIndex).value
            }
        }
    }

    Component {
        id: mappingDelegate

        Frame {
            width: view.width
            contentHeight: pixelIdField.height
            padding: 2

            LabeledTextField {
                id: pixelIdField
                labelText: "Pixel ID for face no. " + index + ":"
                editorText: pixel_id == null ? "" : pixel_id
                onEditingFinished: pixel_id = parseInt(editorText)
                validator: nullableIntValidator
            }
        }
    }

    NullableIntValidator {
        id: nullableIntValidator
        bottom: 0
    }

    IntValidator {
        id: integerValidator
        bottom: 0
    }

    DoubleValidator {
        id: numberValidator
        notation: DoubleValidator.StandardNotation
    }

    states: [
        State {
            name: "Grid"
            PropertyChanges { target: pane; pixelModel: gridModel }
            PropertyChanges { target: view; model: gridModel }
            PropertyChanges { target: view; delegate: gridDelegate }
            PropertyChanges { target: pixelLabel; text: "Pixel grid:" }
        },
        State {
            name: "Mapping"
            PropertyChanges { target: pane; pixelModel: mappingModel }
            PropertyChanges { target: view; model: mappingModel }
            PropertyChanges { target: view; delegate: mappingDelegate }
            PropertyChanges { target: view; height: 200 }
            PropertyChanges { target: view; interactive: true }
            PropertyChanges { target: pixelLabel; text: "Pixel mapping:" }
        }
    ]

}