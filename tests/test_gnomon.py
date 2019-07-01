from PySide2.QtGui import QMatrix4x4, QVector3D, QColor
from mock import Mock

from nexus_constructor.gnomon import Gnomon


def test_GIVEN_cylinder_and_length_WHEN_calling_configure_gnomon_cylinder_THEN_properties_set():

    mock_cylinder_mesh = Mock()
    length = 20

    Gnomon.configure_gnomon_cylinder(mock_cylinder_mesh, length)

    mock_cylinder_mesh.setRadius.assert_called_once_with(length * 0.05)
    mock_cylinder_mesh.setLength.assert_called_once_with(length)
    mock_cylinder_mesh.setRings.assert_called_once_with(2)


def test_GIVEN_cylinder_length_WHEN_calling_create_cylinder_matrices_THEN_correct_matrices_returned():

    length = 10
    half_length = length * 0.5

    expected_x = QMatrix4x4()
    expected_y = QMatrix4x4()
    expected_z = QMatrix4x4()

    expected_x.rotate(270, QVector3D(0, 0, 1))
    expected_x.translate(QVector3D(0, half_length, 0))

    expected_y.translate(QVector3D(0, half_length, 0))

    expected_z.rotate(90, QVector3D(1, 0, 0))
    expected_z.translate(QVector3D(0, half_length, 0))

    actual_x, actual_y, actual_z = Gnomon.create_cylinder_matrices(length)

    assert expected_x == actual_x
    assert expected_y == actual_y
    assert expected_z == actual_z


def test_GIVEN_cone_length_WHEN_calling_create_cone_matrices_THEN_correct_matrices_returned():

    length = 8

    expected_x = QMatrix4x4()
    expected_y = QMatrix4x4()
    expected_z = QMatrix4x4()

    expected_x.rotate(270, QVector3D(0, 0, 1))
    expected_x.translate(QVector3D(0, length, 0))

    expected_y.translate(QVector3D(0, length, 0))

    expected_z.rotate(90, QVector3D(1, 0, 0))
    expected_z.translate(QVector3D(0, length, 0))

    actual_x, actual_y, actual_z = Gnomon.create_cone_matrices(length)

    assert expected_x == actual_x
    assert expected_y == actual_y
    assert expected_z == actual_z


def test_GIVEN_material_and_color_WHEN_calling_prepare_gnomon_material_THEN_properties_set():

    material = Mock()
    color = "red"

    Gnomon.prepare_gnomon_material(material, color)

    material.setAmbient.assert_called_once_with(QColor(color))
    material.setDiffuse.assert_called_once_with(QColor("grey"))
    material.setShininess.assert_called_once_with(0)


def test_GIVEN_mesh_and_length_WHEN_calling_configure_gnomon_cylinder_THEN_properties_set():

    cylinder_mesh = Mock()
    length = 20
    radius = length * 0.05

    Gnomon.configure_gnomon_cylinder(cylinder_mesh, length)

    cylinder_mesh.setRadius.assert_called_once_with(radius)
    cylinder_mesh.setLength.assert_called_once_with(length)
    cylinder_mesh.setRings.assert_called_once_with(2)
