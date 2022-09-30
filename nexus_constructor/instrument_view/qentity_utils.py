from typing import List

from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtGui import QColor

from nexus_constructor.component_type import (
    SAMPLE_CLASS_NAME,
    SLIT_CLASS_NAME,
    SOURCE_CLASS_NAME,
)

MATERIAL_COLORS = {
    SAMPLE_CLASS_NAME: QColor("red"),
    SLIT_CLASS_NAME: QColor("green"),
    SOURCE_CLASS_NAME: QColor("blue"),
}


MATERIAL_DIFFUSE_COLORS = {
    SAMPLE_CLASS_NAME: QColor("grey"),
    SLIT_CLASS_NAME: QColor("darkgreen"),
    SOURCE_CLASS_NAME: QColor("lightblue"),
}


MATERIAL_ALPHA = {
    SAMPLE_CLASS_NAME: 0.5,
    SLIT_CLASS_NAME: 0.75,
    SOURCE_CLASS_NAME: 0.5,
}




class Entity(Qt3DCore.QEntity):
    def __init__(self, parent, picker=True):
        super().__init__(parent)
        self.parent = parent
        
   
        self.clicked = False
        self.inside = False
        self.old_mesh = None

        
        if picker:
            self.picker = Qt3DRender.QObjectPicker()
            self.picker.setHoverEnabled(True)
            self.picker.setDragEnabled(True)
            
            # self.hoover_material = Qt3DExtras.QPhongMaterial(
            #     ambient=QColor("#275fff")
            #     # diffuse=QColor("#99e6ff")
            # )
            self.hoover_material = Qt3DExtras.QGoochMaterial(
                cool=QColor("#275fff"),
                warm=QColor("#99e6ff")
            )
            
            self.picker.entered.connect(self.mouse_enter_event)
            self.picker.exited.connect(self.mouse_leave_event)
            
            # self.picker.clicked.connect(self.mouse_clicked_event)
            # self.picker.released.connect(self.mouse_event)
            
            self.addComponent(self.picker)

        
    def switch_to_highlight(self):
        for c in self.components():
            if type(c) == type(self.hoover_material):
                if c != self.hoover_material:
                    self.true_material = c
                    self.removeComponent(c)
                    self.addComponent(self.hoover_material)
                    
    def switch_to_normal(self):
        for c in self.components():
            if type(c) == type(self.hoover_material):
                self.removeComponent(self.hoover_material)
                self.addComponent(self.true_material)
    
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

                
    # def mouse_clicked_event(self, event):        
    #     self.from_view = True
        


        

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
    components: List[Qt3DCore.QComponent], parent=None, picker=True,
) -> Qt3DCore.QEntity:
    """
    Creates a QEntity and gives it all of the QComponents that are contained in a list.
    """
    entity = Entity(parent, picker)
    for component in components:
        entity.addComponent(component)
    return entity
