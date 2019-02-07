pragma Singleton
import QtQuick 2.0
QtObject {
    // Boolean to indicate that a potentially intensive task is running. Controls appearance of status message in bottom part of window.
    property bool running: false
}