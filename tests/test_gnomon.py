from PySide2.QtGui import QMatrix4x4, QVector3D, QColor, QFont, QVector4D
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


def test_GIVEN_length_WHEN_calling_create_cylinder_matrices_THEN_correct_matrices_returned():

    length = 8

    expected_x = QMatrix4x4()
    expected_y = QMatrix4x4()
    expected_z = QMatrix4x4()

    half_length = length * 0.5

    expected_x.rotate(270, QVector3D(0, 0, 1))
    expected_x.translate(QVector3D(0, half_length, 0))

    expected_y.translate(QVector3D(0, half_length, 0))

    expected_z.rotate(90, QVector3D(1, 0, 0))
    expected_z.translate(QVector3D(0, half_length, 0))

    actual_x, actual_y, actual_z = Gnomon.create_cylinder_matrices(length)

    assert expected_x == actual_x
    assert expected_y == actual_y
    assert expected_z == actual_z


def test_GIVEN_length_WHEN_calling_create_cone_matrices_THEN_correct_matrices_returned():

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


def test_GIVEN_vectors_WHEN_calling_create_axis_label_matrices_THEN_correct_matrices_returned():

    vectors = [QVector3D(1, 0, 0), QVector3D(0, 1, 0), QVector3D(0, 0, 1)]

    expected_x = QMatrix4x4()
    expected_y = QMatrix4x4()
    expected_z = QMatrix4x4()

    expected_x.translate(vectors[0])
    expected_y.translate(vectors[1])
    expected_z.translate(vectors[2])

    actual_x, actual_y, actual_z = Gnomon.create_axis_label_matrices(vectors)

    assert expected_x == actual_x
    assert expected_y == actual_y
    assert expected_z == actual_z


def test_GIVEN_mesh_and_length_WHEN_calling_configure_gnomon_cone_THEN_properties_set():

    cone_mesh = Mock()
    gnomon_cylinder_length = 10

    Gnomon.configure_gnomon_cone(cone_mesh, gnomon_cylinder_length)

    cone_mesh.setLength.assert_called_once_with(gnomon_cylinder_length * 0.3)
    cone_mesh.setBottomRadius.assert_called_once_with(gnomon_cylinder_length * 0.1)
    cone_mesh.setTopRadius.assert_called_once_with(0)


def test_GIVEN_entity_label_and_color_WHEN_calling_set_axis_label_text_THEN_properties_set():

    text_entity = Mock()
    text_label = "X"
    text_color = "green"

    Gnomon.set_axis_label_text(text_entity, text_label, text_color)

    text_entity.setText.assert_called_once_with(text_label)
    text_entity.setHeight.assert_called_once_with(1.2)
    text_entity.setWidth.assert_called_once_with(1)
    text_entity.setColor.assert_called_once_with(QColor(text_color))
    text_entity.setFont.assert_called_once_with(QFont("Courier New", 1))


def test_GIVEN_view_matrix_and_vector_WHEN_calling_create_billboard_transformation_THEN_corect_matrix_returned():

    view_matrix = QMatrix4x4(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
    text_vector = QVector3D(10, 10, 10)

    expected_matrix = view_matrix.transposed()
    expected_matrix.setRow(3, QVector4D())
    expected_matrix.setColumn(3, QVector4D(text_vector, 1))

    actual_matrix = Gnomon.create_billboard_transformation(view_matrix, text_vector)

    assert expected_matrix == actual_matrix
