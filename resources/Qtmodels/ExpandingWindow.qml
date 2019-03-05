import QtQuick.Window 2.11

/*
 * A QtQuick.Window Window that will automatically increase its size in
 * either dimension when it's minimum width or height properties become
 * larger than its current size.
 */

Window {
    onMinimumWidthChanged: {
        width = Math.max(width, minimumWidth)
        width = width // unbind width from minimumWidth so the window won't shrink with it
    }
    onMinimumHeightChanged: {
        height = Math.max(height, minimumHeight)
        height = height // unbind width from minimumWidth so the window won't shrink with it
    }
}
