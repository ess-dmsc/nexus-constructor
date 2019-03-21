import QtQuick.Controls 2.4

ScrollBar  {
    policy: ScrollBar.AsNeeded
    active: true
    onActiveChanged: {
        if (!active) {
        // Have the scrollbar appear without the mouse being over the Flickable
            active = true;
        }
    }
}