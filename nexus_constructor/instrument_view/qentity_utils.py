from typing import Any, List, Tuple, Union

from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtGui import QColor

MATERIAL_DICT = {
    "DEFAULT": {
        "material_type": Qt3DExtras.QGoochMaterial,
        "normal_state": {
            "shadows": QColor("#9f9f9f"),
            "highlights": QColor("#dbdbdb"),
        },
        "hoover_state": {
            "shadows": QColor("#275fff"),
            "highlights": QColor("#99e6ff"),
        },
    },
    "ground": {
        "material_type": Qt3DExtras.QPhongMaterial,
        "normal_state": {
            "shadows": QColor("#f8dd9e"),
            "highlights": QColor("#b69442"),
        },
        "hoover_state": {
            "shadows": QColor("#f8dd9e"),
            "highlights": QColor("#b69442"),
        },
    },
    "NXslit": {
        "material_type": Qt3DExtras.QPhongAlphaMaterial,
        "normal_state": {
            "shadows": QColor("green"),
            "highlights": QColor("darkgreen"),
            "alpha": 0.75,
        },
        "hoover_state": {
            "shadows": QColor("green"),
            "highlights": QColor("darkgreen"),
            "alpha": 1.0,
        },
    },
    "NXsample": {
        "material_type": Qt3DExtras.QPhongAlphaMaterial,
        "normal_state": {
            "shadows": QColor("red"),
            "highlights": QColor("grey"),
            "alpha": 0.5,
        },
        "hoover_state": {
            "shadows": QColor("red"),
            "highlights": QColor("grey"),
            "alpha": 0.75,
        },
    },
    "NXsource": {
        "material_type": Qt3DExtras.QPhongAlphaMaterial,
        "normal_state": {
            "shadows": QColor("blue"),
            "highlights": QColor("lightblue"),
            "alpha": 0.5,
        },
        "hoover_state": {
            "shadows": QColor("blue"),
            "highlights": QColor("lightblue"),
            "alpha": 0.75,
        },
    },
    "x_material": {
        "material_type": Qt3DExtras.QPhongMaterial,
        "normal_state": {
            "shadows": QColor(255, 0, 0),
            "highlights": QColor(255, 100, 100),
        },
        "hoover_state": {
            "shadows": QColor(255, 0, 0),
            "highlights": QColor(255, 100, 100),
        },
    },
    "y_material": {
        "material_type": Qt3DExtras.QPhongMaterial,
        "normal_state": {
            "shadows": QColor(0, 255, 0),
            "highlights": QColor(100, 255, 100),
        },
        "hoover_state": {
            "shadows": QColor(0, 255, 0),
            "highlights": QColor(100, 255, 100),
        },
    },
    "z_material": {
        "material_type": Qt3DExtras.QPhongMaterial,
        "normal_state": {
            "shadows": QColor(0, 0, 255),
            "highlights": QColor(100, 100, 255),
        },
        "hoover_state": {
            "shadows": QColor(0, 0, 255),
            "highlights": QColor(100, 100, 255),
        },
    },
    "beam_material": {
        "material_type": Qt3DExtras.QPhongAlphaMaterial,
        "normal_state": {
            "shadows": QColor("blue"),
            "highlights": QColor("lightblue"),
            "alpha": 0.5,
        },
        "hoover_state": {
            "shadows": QColor("blue"),
            "highlights": QColor("lightblue"),
            "alpha": 0.75,
        },
    },
    "neutron_material": {
        "material_type": Qt3DExtras.QPhongMaterial,
        "normal_state": {
            "shadows": QColor("black"),
            "highlights": QColor("grey"),
        },
        "hoover_state": {
            "shadows": QColor("black"),
            "highlights": QColor("grey"),
        },
    },
}


class Entity(Qt3DCore.QEntity):
    def __init__(self, parent, picker=True):
        super().__init__(parent)
        self.parent = parent

        self.clicked = False
        self.inside = False
        self.old_mesh = None
        self.default_material = None
        self.hoover_material = None
        self.material_family = None

        if picker:
            self.picker = Qt3DRender.QObjectPicker()
            self.picker.setHoverEnabled(True)
            self.picker.setDragEnabled(True)
            self.picker.entered.connect(self.mouse_enter_event)
            self.picker.exited.connect(self.mouse_leave_event)
            self.addComponent(self.picker)

    def switch_to_highlight(self):
        try:
            self.removeComponent(self.default_material)
            self.addComponent(self.hoover_material)
        except Exception:
            pass

    def switch_to_normal(self):
        try:
            self.removeComponent(self.hoover_material)
            self.addComponent(self.default_material)
        except Exception:
            pass

    def mouse_enter_event(self):
        self.inside = True
        self.switch_to_highlight()

    def mouse_leave_event(self):
        self.inside = False
        if self.clicked:
            return
        self.switch_to_normal()

    def switch_mesh(self, new_mesh):
        for c in self.components():
            if type(c) == type(new_mesh):
                if c == new_mesh:
                    return
                self.old_mesh = c
                self.removeComponent(c)
                self.addComponent(new_mesh)


# def create_material(
#     ambient: QColor,
#     diffuse: QColor,
#     parent: Qt3DCore.QEntity,
#     alpha: float = None,
#     remove_shininess: bool = False,
# ) -> Qt3DRender.QMaterial:
#     """
#     Creates a material and then sets its ambient, diffuse, alpha (if provided) properties. Sets shininess to zero if
#     instructed.
#     :param ambient: The desired ambient colour of the material.
#     :param diffuse: The desired diffuse colour of the material.
#     :param alpha: The desired alpha value of the material. Optional argument as not all material-types have this
#                   property.
#     :param remove_shininess: Boolean indicating whether or not to remove shininess. This is used for the gnomon.
#     :return A material that is now able to be added to an entity.
#     """
#
#     if alpha is not None:
#         material = Qt3DExtras.QPhongAlphaMaterial(parent)
#         material.setAlpha(alpha)
#     else:
#         material = Qt3DExtras.QPhongMaterial(parent)
#
#     if remove_shininess:
#         material.setShininess(0)
#
#     material.setAmbient(ambient)
#     material.setDiffuse(diffuse)
#
#     return material


def create_material(
    material_name: str,
    parent: Qt3DCore.QEntity,
    remove_shininess: bool = False,
) -> Tuple[
    Union[Union[Qt3DExtras.QPhongAlphaMaterial, Qt3DExtras.QGoochMaterial], Any], Any
]:
    if material_name not in MATERIAL_DICT.keys():
        normal_material = MATERIAL_DICT["DEFAULT"]["material_type"].__call__(parent)
        hoover_material = MATERIAL_DICT["DEFAULT"]["material_type"].__call__(parent)
        normal_material.setCool(MATERIAL_DICT["DEFAULT"]["normal_state"]["shadows"])
        normal_material.setWarm(MATERIAL_DICT["DEFAULT"]["normal_state"]["highlights"])
        hoover_material.setCool(MATERIAL_DICT["DEFAULT"]["hoover_state"]["shadows"])
        hoover_material.setWarm(MATERIAL_DICT["DEFAULT"]["hoover_state"]["highlights"])
        material_family = "DEFAULT"
    else:
        normal_material = MATERIAL_DICT[material_name]["material_type"].__call__(parent)
        hoover_material = MATERIAL_DICT[material_name]["material_type"].__call__(parent)
        material_family = material_name
        if isinstance(normal_material, Qt3DExtras.QGoochMaterial):
            normal_material.setCool(
                MATERIAL_DICT[material_name]["normal_state"]["shadows"]
            )
            normal_material.setWarm(
                MATERIAL_DICT[material_name]["normal_state"]["highlights"]
            )
            hoover_material.setCool(
                MATERIAL_DICT[material_name]["hoover_state"]["shadows"]
            )
            hoover_material.setWarm(
                MATERIAL_DICT[material_name]["hoover_state"]["highlights"]
            )
        elif isinstance(
            normal_material, (Qt3DExtras.QPhongMaterial, Qt3DExtras.QPhongAlphaMaterial)
        ):
            normal_material.setAmbient(
                MATERIAL_DICT[material_name]["normal_state"]["shadows"]
            )
            normal_material.setDiffuse(
                MATERIAL_DICT[material_name]["normal_state"]["highlights"]
            )
            hoover_material.setAmbient(
                MATERIAL_DICT[material_name]["hoover_state"]["shadows"]
            )
            hoover_material.setDiffuse(
                MATERIAL_DICT[material_name]["hoover_state"]["highlights"]
            )

        if isinstance(normal_material, Qt3DExtras.QPhongAlphaMaterial):
            normal_material.setAlpha(
                MATERIAL_DICT[material_name]["normal_state"]["alpha"]
            )
            hoover_material.setAlpha(
                MATERIAL_DICT[material_name]["hoover_state"]["alpha"]
            )

    if remove_shininess:
        normal_material.setShininess(0)
        hoover_material.setShininess(0)

    return normal_material, hoover_material, material_family


def create_qentity(
    components: List[Qt3DCore.QComponent],
    parent=None,
    picker=True,
) -> Qt3DCore.QEntity:
    """
    Creates a QEntity and gives it all of the QComponents that are contained in a list.
    """
    entity = Entity(parent, picker)
    for component in components:
        entity.addComponent(component)
    return entity
