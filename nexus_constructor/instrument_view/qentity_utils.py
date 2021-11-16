from typing import List

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtGui import QColor


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


from PySide2.QtGui import QColor, QMatrix4x4, QVector3D


def get_nx_source(gnomon_root_entity, neutron_animation_length=6):
    cylinder_mesh = Qt3DExtras.QCylinderMesh(gnomon_root_entity)
    cylinder_transform = Qt3DCore.QTransform(gnomon_root_entity)
    set_cylinder_mesh_dimensions(cylinder_mesh, 1.5, neutron_animation_length, 2)
    set_beam_transform(cylinder_transform, neutron_animation_length)
    beam_material = create_material(
        QColor("blue"), QColor("lightblue"), gnomon_root_entity, alpha=0.5
    )
    return create_qentity(
        [cylinder_mesh, beam_material, cylinder_transform], gnomon_root_entity
    )


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
