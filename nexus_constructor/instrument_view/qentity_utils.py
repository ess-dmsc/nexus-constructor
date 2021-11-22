from typing import List

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtGui import QColor, QMatrix4x4, QVector3D


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


def create_neutron_source(root_entity, neutron_animation_length=4):
    cone_mesh = Qt3DExtras.QConeMesh(root_entity)
    cone_transform = Qt3DCore.QTransform(root_entity)
    set_cone_dimension(cone_mesh, 0.5, 1.0, neutron_animation_length, 50, 20)
    set_cone_transform(cone_transform, neutron_animation_length)
    material = create_material(
        QColor("#928327"), QColor("#928327"), root_entity, alpha=0.5
    )
    create_qentity([cone_mesh, material, cone_transform], root_entity)
    return root_entity


def set_cone_dimension(cone_mesh, top_radius, bottom_radius, length, rings, slices):
    cone_mesh.setTopRadius(top_radius)
    cone_mesh.setBottomRadius(bottom_radius)
    cone_mesh.setLength(length)
    cone_mesh.setRings(rings)
    cone_mesh.setSlices(slices)


def set_cone_transform(cone_transform, neutron_animation_distance):
    # pass
    matrix = QMatrix4x4()
    matrix.rotate(90, QVector3D(1, 0, 0))
    matrix.translate(QVector3D(0, neutron_animation_distance * 0.5, 0))
    cone_transform.setMatrix(matrix)
