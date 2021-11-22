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


class QSource:
    def __init__(self, root_entity=None) -> None:
        self.root_entity = root_entity
        self._child_entitites = []
        self._source = None
        self._neutrons = []

        self.neutron_animation_length = 4
        self.num_neutrons = 9
        self.create_neutron_source()
        self.setup_neutrons()

    def create_neutron_source(
        self,
    ):
        cone_mesh = Qt3DExtras.QConeMesh(self.root_entity)
        cone_transform = Qt3DCore.QTransform(self.root_entity)
        set_cone_dimension(cone_mesh, 1.0, 1.0, self.neutron_animation_length, 50, 20)
        set_cone_transform(cone_transform, self.neutron_animation_length)
        material = create_material(
            QColor("#928327"), QColor("#928327"), self.root_entity, alpha=0.5
        )

        # self._child_entitites["source"] = create_qentity(
        #         [cone_mesh, material, cone_transform], self.root_entity
        #     )
        self._child_entitites.append(
            create_qentity([cone_mesh, material, cone_transform], self.root_entity)
        )

    def setup_neutrons(self):
        x_offsets = [0, 0, 0, 2, -2, 1.4, 1.4, -1.4, -1.4]
        y_offsets = [0, 2, -2, 0, 0, 1.4, -1.4, 1.4, -1.4]
        time_span_offsets = [0, -5, -7, 5, 7, 19, -19, 23, -23]

        neutron_radius = 1.5

        for i in range(9):
            mesh = Qt3DExtras.QSphereMesh(self.root_entity)
            self.set_sphere_mesh_radius(mesh, neutron_radius)

            transform = Qt3DCore.QTransform(self.root_entity)
            neutron_animation_controller = NeutronAnimationController(
                x_offsets[i] * 0.5, y_offsets[i] * 0.5, transform
            )
            neutron_animation_controller.set_target(transform)

            neutron_animation = QPropertyAnimation(transform)
            self.set_neutron_animation_properties(
                neutron_animation,
                neutron_animation_controller,
                self.neutron_animation_length,
                time_span_offsets[i],
            )
            neutron_material = create_material(
                QColor("black"), QColor("grey"), self.root_entity
            )
            self._child_entitites.append(
                create_qentity([mesh, neutron_material, transform], self.root_entity)
            )

    @staticmethod
    def set_sphere_mesh_radius(sphere_mesh, radius):
        sphere_mesh.setRadius(radius)

    def setParent(self, value=None):
        for child in self._child_entitites:
            child.setParent(value)

    def addComponent(self, component):
        print(component)
        component.setShareable(True)

        for neutron in self._child_entitites:
            neutron.addComponent(component)

        # Redo rotation transformation on source
        matrix_ = component.matrix()
        blah = QMatrix4x4()
        blah.rotate(90, QVector3D(1, 0, 0))
        blah.translate(QVector3D(0, self.neutron_animation_length * 0.5, 0))
        matrix = matrix_ * blah
        component.setMatrix(matrix)

        blah = QMatrix4x4()
        blah.rotate(90, QVector3D(1, 1, 0))
        blah.translate(QVector3D(0, self.neutron_animation_length * 0.5, 0))
        matrix_2 = matrix_ * blah
        #
        for index, child in enumerate(self._child_entitites):
            if index == 0:
                child.addComponent(component)
            else:
                component.setMatrix(matrix_2)
                child.addComponent(component)

    def removeComponent(self, component):
        for child in self._child_entitites:
            child.removeComponent(component)

    @staticmethod
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
