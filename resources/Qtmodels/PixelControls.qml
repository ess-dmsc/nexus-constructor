import QtQuick 2.11
import QtQuick.Controls 2.4
import MyModels 1.0
import MyValidators 1.0

Item {
    property var pixelModel

    id: pane
    implicitHeight: pixelLabel.height + viewFrame.implicitHeight
    width: viewFrame.width
    implicitWidth: viewFrame.implicitWidth

    signal layoutChanged()

    function restartMapping(geometryModel){
        onGeometryModelChanged: mappingModel.restart_mapping(geometryModel)
    }

    Label {
        id: pixelLabel
        anchors.top: parent.top
        anchors.left: parent.left
        height: 0
    }

    Frame {
        id: viewFrame
        anchors.top: pixelLabel.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        contentHeight: view.height
        contentWidth: view.implicitWidth
        padding: 1

        ListView {
            id: view
            anchors.left: parent.left
            height: contentHeight
            width: parent.width
            interactive: false
            clip: true
            ScrollBar.vertical: bar
            boundsBehavior: Flickable.StopAtBounds
        }

        ActiveScrollBar {
            id: bar
            anchors {
                left: view.right
                top: view.top
                bottom: view.bottom
            }
        }
    }

    PixelGridModel {
        id: gridModel
        onDataChanged: pane.layoutChanged()
    }

    PixelMappingModel {
        id: mappingModel
    }

    SinglePixelModel {
        id: singlePixelModel
    }

    Component {
        id: gridDelegate

        Pane {
            id: gridFields
            width: view.width
            contentHeight: rowsField.height +
                columnsField.height +
                firstIdField.height +
                cornerPicker.height +
                directionPicker.height
            contentWidth: Math.max(
                rowsField.implicitWidth + rowHeightField.implicitWidth,
                columnsField.implicitWidth + columnWidthField.implicitWidth
            )

            Component.onCompleted: view.implicitWidth = gridFields.implicitWidth

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
                editorText: column_width
                onEditingFinished: column_width = parseFloat(editorText)
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
            id: mappingItem
            width: view.width
            contentWidth: pixelIdField.implicitWidth
            contentHeight: pixelIdField.implicitHeight
            padding: 2

            Component.onCompleted: view.implicitWidth = mappingItem.implicitWidth

            LabeledTextField {
                id: pixelIdField
                labelText: "Pixel ID for face no. " + index + ":"
                editorText: mappingModel.pixel_id == null ? "" : mappingModel.pixel_id
                onEditingFinished: mappingModel.pixel_id = parseInt(editorText)
                validator: nullableIntValidator
            }
        }
    }

    Component {
        id: singlePixelDelegate

        LabeledTextField {
            id: pixelIdField
            anchors.right: parent.right
            padding: 10
            labelText: "Detector ID:"
            editorText: pixel_id == null ? "" : pixel_id
            onEditingFinished: pixel_id = parseInt(editorText)
            validator: nullableIntValidator
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
            PropertyChanges { target: pixelLabel; height: implicitHeight }
        },
        State {
            name: "Mapping"
            PropertyChanges { target: pane; pixelModel: mappingModel }
            PropertyChanges { target: view; model: mappingModel }
            PropertyChanges { target: view; delegate: mappingDelegate }
            PropertyChanges { target: view; height: 200 }
            PropertyChanges { target: view; interactive: true }
            PropertyChanges { target: pixelLabel; text: "Pixel mapping:" }
            PropertyChanges { target: pixelLabel; height: implicitHeight }
        },
        State {
            name: "SinglePixel"
            PropertyChanges { target: pane; pixelModel: singlePixelModel }
            PropertyChanges { target: view; model: singlePixelModel }
            PropertyChanges { target: view; delegate: singlePixelDelegate }
            PropertyChanges { target: pixelLabel; text: "Pixel data:" }
            PropertyChanges { target: pixelLabel; height: implicitHeight }

        }
    ]

}
