from typing import List

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtCore import QPropertyAnimation
from PySide2.QtGui import QColor, QMatrix4x4, QVector3D

from nexus_constructor.instrument_view.neutron_animation_controller import (
    NeutronAnimationController,
)


def create_material(
    ambient: QColor,
    diffuse: QColor,
    parent: Qt3DCore.QEntity,
    alpha: float = None,
    remove_shininess: bool = False,
) -> Qt3DRender.QMaterial:
    """
    Creates a material and then sets its ambient, diffuse, alpha (if provided) properties. Sets shininess to zero if
    instructed.
    :param ambient: The desired ambient colour of the material.
    :param diffuse: The desired diffuse colour of the material.
    :param alpha: The desired alpha value of the material. Optional argument as not all material-types have this
                  property.
    :param remove_shininess: Boolean indicating whether or not to remove shininess. This is used for the gnomon.
    :return A material that is now able to be added to an entity.
    """

    if alpha is not None:
        material = Qt3DExtras.QPhongAlphaMaterial(parent)
        material.setAlpha(alpha)
    else:
        material = Qt3DExtras.QPhongMaterial(parent)

    if remove_shininess:
        material.setShininess(0)

    material.setAmbient(ambient)
    material.setDiffuse(diffuse)

    return material


def create_qentity(
    components: List[Qt3DCore.QComponent], parent=None
) -> Qt3DCore.QEntity:
    """
    Creates a QEntity and gives it all of the QComponents that are contained in a list.
    """
    entity = Qt3DCore.QEntity(parent)
    for component in components:
        entity.addComponent(component)
    return entity


def get_nx_source(gnomon_root_entity, neutron_animation_length=4):
    setup_neutrons(gnomon_root_entity, neutron_animation_length)
    cylinder_mesh = Qt3DExtras.QCylinderMesh(gnomon_root_entity)
    cylinder_transform = Qt3DCore.QTransform(gnomon_root_entity)
    set_cylinder_mesh_dimensions(cylinder_mesh, 1.5, neutron_animation_length, 2)
    set_beam_transform(cylinder_transform, neutron_animation_length)
    beam_material = create_material(
        QColor("blue"), QColor("lightblue"), gnomon_root_entity, alpha=0.5
    )
    create_qentity(
        [cylinder_mesh, beam_material, cylinder_transform], gnomon_root_entity
    )
    return gnomon_root_entity


def set_cylinder_mesh_dimensions(cylinder_mesh, radius, length, rings):
    """
    Sets the dimensions of a cylinder mesh.
    :param cylinder_mesh: The cylinder mesh to modify.
    :param radius: The desired radius.
    :param length: The desired length.
    :param rings: The desired number of rings.
    """
    cylinder_mesh.setRadius(radius)
    cylinder_mesh.setLength(length)
    cylinder_mesh.setRings(rings)


def set_beam_transform(cylinder_transform, neutron_animation_distance):
    """
    Configures the transform for the beam cylinder by giving it a matrix. The matrix will turn the cylinder sideways
    and then move it "backwards" in the z-direction by 20 units so that it ends at the location of the sample.
    :param cylinder_transform: A QTransform object.
    :param neutron_animation_distance: The distance that the neutron travels during its animation.
    """
    cylinder_matrix = QMatrix4x4()
    cylinder_matrix.rotate(90, QVector3D(1, 0, 0))
    cylinder_matrix.translate(QVector3D(0, neutron_animation_distance * 0.5, 0))

    cylinder_transform.setMatrix(cylinder_matrix)


def set_neutron_animation_properties(
    neutron_animation,
    neutron_animation_controller,
    animation_distance,
    time_span_offset,
):
    """
    Prepares a QPropertyAnimation for a neutron by giving it a target, a distance, and loop settings.
    :param neutron_animation: The QPropertyAnimation to be configured.
    :param neutron_animation_controller: The related animation controller object.
    :param animation_distance: The starting distance of the neutron.
    :param time_span_offset: The offset that allows the neutron to move at a different time from other neutrons.
    """
    neutron_animation.setTargetObject(neutron_animation_controller)
    neutron_animation.setPropertyName(b"distance")
    neutron_animation.setStartValue(0)
    neutron_animation.setEndValue(animation_distance)
    neutron_animation.setDuration(500 + time_span_offset)
    neutron_animation.setLoopCount(-1)
    neutron_animation.start()


def setup_neutrons(gnomon_root_entity, neutron_animation_distance):
    """
    Sets up the neutrons and their animations by preparing their meshes and then giving offset and
    distance parameters to an animation controller.
    """

    # Create lists of x, y, and time offsets for the neutron animations
    x_offsets = [0, 0, 0, 2, -2, 1.4, 1.4, -1.4, -1.4]
    y_offsets = [0, 2, -2, 0, 0, 1.4, -1.4, 1.4, -1.4]
    time_span_offsets = [0, -5, -7, 5, 7, 19, -19, 23, -23]

    neutron_radius = 1.5

    for i in range(9):
        mesh = Qt3DExtras.QSphereMesh(gnomon_root_entity)
        set_sphere_mesh_radius(mesh, neutron_radius)

        transform = Qt3DCore.QTransform(gnomon_root_entity)
        neutron_animation_controller = NeutronAnimationController(
            x_offsets[i] * 0.5, y_offsets[i] * 0.5, transform
        )
        neutron_animation_controller.set_target(transform)

        neutron_animation = QPropertyAnimation(transform)
        set_neutron_animation_properties(
            neutron_animation,
            neutron_animation_controller,
            neutron_animation_distance,
            time_span_offsets[i],
        )

        neutron_material = create_material(
            QColor("black"), QColor("grey"), gnomon_root_entity
        )

        create_qentity([mesh, neutron_material, transform], gnomon_root_entity)
    return gnomon_root_entity


def set_sphere_mesh_radius(sphere_mesh, radius):
    """
    Sets the radius of a sphere mesh.
    :param sphere_mesh: The sphere mesh to modify.
    :param radius: The desired radius.
    """
    sphere_mesh.setRadius(radius)
