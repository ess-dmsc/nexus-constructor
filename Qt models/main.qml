import QtQuick 2.0

Rectangle {
  width: 200; height: 200

  ListView {
    model: PixelModel {}
    delegate: pixelDelegate
    anchors.fill: parent
  }

  Component {
    id: pixelDelegate
    Row {
      Text { text: "<b>Pixel name:</b>" + name + " <b>Faces:</b>" }
      Repeater {
        model: faces
        Text { text: face + "," }
      }
    }
  }
}
