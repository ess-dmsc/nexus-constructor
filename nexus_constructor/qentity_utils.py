from typing import List

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtGui import QColor


def set_material_properties(
    material: Qt3DRender.QMaterial,
    ambient: QColor,
    diffuse: QColor,
    alpha: float = None,
    remove_shininess: bool = False,
) -> None:
    """
    Set the ambient, diffuse, and alpha properties of a material.
    :param material: The material to be modified.
    :param ambient: The desired ambient colour of the material.
    :param diffuse: The desired diffuse colour of the material.
    :param alpha: The desired alpha value of the material. Optional argument as not all material-types have this
                  property.
    :param remove_shininess: Boolean indicating whether or not to remove shininess. This is used for the gnomon.
    """
    material.setAmbient(ambient)
    material.setDiffuse(diffuse)

    if alpha is not None:
        material.setAlpha(alpha)

    if remove_shininess:
        material.setShininess(0)


def add_qcomponents_to_entity(
    entity: Qt3DCore.QEntity, components: List[Qt3DCore.QComponent]
) -> None:
    """
    Takes a QEntity and gives it all of the QComponents that are contained in a list.
    """
    for component in components:
        entity.addComponent(component)
