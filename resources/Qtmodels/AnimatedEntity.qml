import Qt3D.Core 2.0
import Qt3D.Extras 2.0
import Qt3D.Input 2.0
import Qt3D.Render 2.0
import QtQuick 2.11
import MyModels 1.0

Entity {
    id: sceneRoot

    property InstrumentModel instrument
    property alias camera: camera
    property real negativeOne: -1.0

    Camera {
        id: camera
        projectionType: CameraLens.PerspectiveProjection
        fieldOfView: 45
        nearPlane : 0.1
        farPlane : 1000.0
        position: Qt.vector3d( 6.0, 8.0, 30.0 )
        upVector: Qt.vector3d( 0.0, 1.0, 0.0 )
        viewCenter: Qt.vector3d( 0.0, 0.0, 0.0 )
    }

    function updateView() {
        camera.translateWorld(camera.position.times(-1.0))
        console.log(camera.position)
        camera.viewAll()
    }

    FirstPersonCameraController { camera: camera
     linearSpeed: 20}

    components: [
        RenderSettings {
            activeFrameGraph: RenderSurfaceSelector {
                ClearBuffers {
                    buffers: ClearBuffers.ColorDepthBuffer
                    clearColor: "lightgrey"

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
        },
        InputSettings { }
    ]

    PhongMaterial {
        id: greyMaterial
        ambient: "black"
        diffuse: "grey"
    }

    PhongMaterial {
        id: redMaterial
        ambient: "red"
        diffuse: "#b00"
    }

    PhongAlphaMaterial {
        id: beamMaterial
        ambient: "blue"
        diffuse: "lightblue"
        alpha: 0.5
    }

    PhongMaterial {
        id: greenMaterial
        ambient: "green"
        diffuse: "green"
    }

    SphereMesh {
        id: sphereMesh
        radius: 3
    }

    Neutron {
        material: greyMaterial
        mesh: sphereMesh
    }

    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        yOffset: 2
        timespanOffset: -5
    }
    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        yOffset: -2
        timespanOffset: -7
    }
    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        xOffset: 2
        timespanOffset: 5
    }
    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        xOffset: -2
        timespanOffset: 7
    }

    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        xOffset: 1.4
        yOffset: 1.4
        timespanOffset: 19
    }
    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        xOffset: 1.4
        yOffset: -1.4
        timespanOffset: -19
    }
    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        xOffset: -1.4
        yOffset: 1.4
        timespanOffset: 23
    }
    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        xOffset: -1.4
        yOffset: -1.4
        timespanOffset: -23
    }

    CylinderMesh {
        id: cylinderMesh
        length: 40
        radius: 2.5
        rings: 2
    }

    NodeInstantiator  {
        id: componentRenderList
        model: instrument

        Entity {
            id: repeaterEntity
            Transform {
                id: repeaterTransform
                matrix: transform_matrix
            }
            components: [
                mesh,
                index == 0 ? redMaterial : greenMaterial,
                repeaterTransform
            ]
        }
    }

    Transform {
        id: beamTransform
        matrix: {
            var m = Qt.matrix4x4()
            m.rotate(270.0, Qt.vector3d(1,0,0))
            m.translate(Qt.vector3d(0, 20, 0))
            return m;
        }
    }

    Entity {
        id: beamEntity
        components: [ cylinderMesh, beamMaterial, beamTransform ]
    }
}
