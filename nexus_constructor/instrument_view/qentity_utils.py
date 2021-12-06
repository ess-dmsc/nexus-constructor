from typing import List

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtGui import QColor

from nexus_constructor.component_type import SAMPLE_CLASS_NAME, SOURCE_CLASS_NAME

MATERIAL_COLORS = {
    SAMPLE_CLASS_NAME: QColor("red"),
    SOURCE_CLASS_NAME: QColor("blue"),
}


MATERIAL_DIFFUSE_COLORS = {
    SAMPLE_CLASS_NAME: QColor("grey"),
    SOURCE_CLASS_NAME: QColor("lightblue"),
}


MATERIAL_ALPHA = {
    SAMPLE_CLASS_NAME: 0.5,
    SOURCE_CLASS_NAME: 0.5,
}


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
