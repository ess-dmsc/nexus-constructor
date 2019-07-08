from typing import List

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtGui import QColor


def create_material(
    ambient: QColor,
    diffuse: QColor,
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
        material = Qt3DExtras.QPhongAlphaMaterial()
        material.setAlpha(alpha)
    else:
        material = Qt3DExtras.QPhongMaterial()

    if remove_shininess:
        material.setShininess(0)

    material.setAmbient(ambient)
    material.setDiffuse(diffuse)

    return material


def add_qcomponents_to_entity(
    entity: Qt3DCore.QEntity, components: List[Qt3DCore.QComponent]
):
    """
    Takes a QEntity and gives it all of the QComponents that are contained in a list.
    """
    for component in components:
        entity.addComponent(component)
