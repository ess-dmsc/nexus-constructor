pragma Singleton
import QtQuick 2.0
QtObject {
    // Boolean to indicate that the units provided for creating a cylinder were valid
    property bool validCylinderUnits: false
    readonly property string invalidUnitsText: "Units not recognised. Please enter a different type."
}
