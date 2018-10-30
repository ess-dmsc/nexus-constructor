import Qt3D.Core 2.0
import Qt3D.Extras 2.0
import Qt3D.Input 2.0
import Qt3D.Render 2.0
import QtQuick 2.11
import MyModels 1.0

Entity {
    id: sceneRoot

    property InstrumentModel instrument

    Camera {
        id: camera
        projectionType: CameraLens.PerspectiveProjection
        fieldOfView: 45
        nearPlane : 0.1
        farPlane : 1000.0
        position: Qt.vector3d( 0.0, 0.0, 40.0 )
        upVector: Qt.vector3d( 0.0, 1.0, 0.0 )
        viewCenter: Qt.vector3d( 0.0, 0.0, 0.0 )
    }

    FirstPersonCameraController { camera: camera }

    components: [
        RenderSettings {
            activeFrameGraph: ForwardRenderer {
                camera: camera
                clearColor: "lightgrey"
            }
        },
        InputSettings { }
    ]

    PhongMaterial {
        id: greyMaterial
        ambient: "grey"
        diffuse: "grey"
    }

    PhongMaterial {
        id: redMaterial
        ambient: "red"
        diffuse: "red"
    }

    PhongAlphaMaterial {
        id: beamMaterial
        ambient: "blue"
        diffuse: "blue"
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
        zOffset: 2
        timespanOffset: 5
    }
    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        zOffset: -2
        timespanOffset: 7
    }

    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        yOffset: 1.4
        zOffset: 1.4
        timespanOffset: 19
    }
    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        yOffset: -1.4
        zOffset: 1.4
        timespanOffset: -19
    }
    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        yOffset: 1.4
        zOffset: -1.4
        timespanOffset: 23
    }
    Neutron {
        material: greyMaterial
        mesh: sphereMesh
        yOffset: -1.4
        zOffset: -1.4
        timespanOffset: -23
    }

    CylinderMesh {
        id: cylinderMesh
        length: 40
        radius: 2.5
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
            m.rotate(270.0, Qt.vector3d(0,0,1))
            m.translate(Qt.vector3d(0, 20, 0))
            return m;
        }
    }

    Entity {
        id: beamEntity
        components: [ cylinderMesh, beamMaterial, beamTransform ]
    }
}
