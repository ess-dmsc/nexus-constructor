import Qt3D.Core 2.0
import Qt3D.Extras 2.0
import Qt3D.Render 2.0
import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Scene3D 2.0

Item {

    property Camera targetCamera
    readonly property color xColor: "red"
    readonly property color yColor: "green"
    readonly property color zColor: "blue"

    Scene3D {

        anchors.fill: parent
        cameraAspectRatioMode: Scene3D.AutomaticAspectRatio

        Entity {

            Camera {
                id: camera
                projectionType: targetCamera.projectionType
                fieldOfView: targetCamera.fieldOfView
                nearPlane : 0.1
                farPlane : 10.0
                position: targetCamera.position.minus(targetCamera.viewCenter).normalized().times(3)
                upVector: targetCamera.upVector
                viewCenter: Qt.vector3d( 0.0, 0.0, 0.0 )
            }

            components: [
                RenderSettings {
                    activeFrameGraph: RenderSurfaceSelector {
                        ClearBuffers {
                            buffers: ClearBuffers.ColorDepthBuffer
                            clearColor: "transparent"

                            CameraSelector {
                                camera: camera
                                RenderStateSet {
                                    renderStates: [
                                        CullFace { mode: CullFace.NoCulling },
                                        DepthTest { depthFunction: DepthTest.LessOrEqual}
                                    ]
                                }
                            }
                        }
                    }
                }
            ]

            PhongMaterial {
                id: xMaterial
                ambient: xColor
                diffuse: xColor
                shininess: 0
            }

            PhongMaterial {
                id: yMaterial
                ambient: yColor
                diffuse: yColor
                shininess: 0
            }

            PhongMaterial {
                id: zMaterial
                ambient: zColor
                diffuse: zColor
                shininess: 0
            }

            CylinderMesh {
                id: cylinderMesh
                length: 1
                radius: 0.05
                rings: 2
            }

            // cylinder mesh axis is y aligned, origin in center
            Transform {
                id: xTransform
                matrix: {
                    var matrix = Qt.matrix4x4()
                    matrix.rotate(270.0, Qt.vector3d(0,0,1))
                    matrix.translate(Qt.vector3d(0, 0.5, 0))
                    return matrix;
                }
            }

            Transform {
                id: yTransform
                matrix: {
                    var matrix = Qt.matrix4x4()
                    matrix.translate(Qt.vector3d(0, 0.5, 0))
                    return matrix;
                }
            }

            Transform {
                id: zTransform
                matrix: {
                    var matrix = Qt.matrix4x4()
                    matrix.rotate(90.0, Qt.vector3d(1,0,0))
                    matrix.translate(Qt.vector3d(0, 0.5, 0))
                    return matrix;
                }
            }

            Entity {
                id: xAxis
                components: [ cylinderMesh, xMaterial, xTransform ]
            }

            Entity {
                id: yAxis
                components: [ cylinderMesh, yMaterial, yTransform ]
            }

            Entity {
                id: zAxis
                components: [ cylinderMesh, zMaterial, zTransform ]
            }
        }
    }

    Label {
        id: legendX
        text: "X"
        color: xColor
        anchors.bottom: parent.bottom
        anchors.right: legendY.left
    }
    Label {
        id: legendY
        text: " Y "
        color: yColor
        anchors.bottom: parent.bottom
        anchors.right: legendZ.left
    }
    Label {
        id: legendZ
        text: "Z"
        color: zColor
        anchors.bottom: parent.bottom
        anchors.right: parent.right
    }
}
