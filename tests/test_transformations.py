from nexus_constructor.transformations import (
    Rotation,
    Translation,
    Transformation,
    QVector3D,
)
from pytest import raises

transform_type = "Transformation"
rotation_type = "Rotation"
translation_type = "Translation"


def test_GIVEN_angle_WHEN_creating_rotation_THEN_angle_is_set_correctly():
    angle = 180
    transformation = Rotation(name="", axis=QVector3D(1, 0, 0), angle=angle)
    assert transformation.angle == angle


def test_GIVEN_axis_WHEN_creating_rotation_THEN_axis_is_set_correctly():
    axis = QVector3D(1, 0, 0)
    transformation = Rotation(name="", axis=axis)
    assert transformation.axis.toTuple() == axis.toTuple()


def test_GIVEN_vector_WHEN_creating_translation_THEN_translation_is_set_correctly():
    vector = QVector3D(1, 1, 1)
    transformation = Translation(name="", vector=vector)
    assert transformation.vector.toTuple() == vector.toTuple()


def test_GIVEN_name_WHEN_creating_transformation_THEN_name_is_correct():
    name = "hi"
    transformation = Transformation(name=name)
    assert transformation.name == name


def test_GIVEN_name_WHEN_creating_rotation_THEN_name_is_correct():
    name = "rotationofsomesort"
    transformation = Rotation(name=name, axis=QVector3D(1, 0, 0), angle=1)
    assert transformation.name == name


def test_GIVEN_name_WHEN_creating_translation_THEN_name_is_correct():
    name = "translateme"
    transformation = Translation(name=name, vector=QVector3D(1, 0, 0))
    assert transformation.name == name


def test_GIVEN_empty_vector_for_axis_WHEN_creating_rotation_THEN_throws():
    with raises(ValueError):
        Rotation(name="", axis=QVector3D(0, 0, 0), angle=1)


def test_GIVEN_nothing_WHEN_creating_rotation_THEN_transfomation_type_is_correct():
    transformation = Rotation(name="", angle=0, axis=QVector3D(1, 0, 0))
    assert transformation.type == rotation_type


def test_GIVEN_nothing_WHEN_creating_translation_THEN_transformation_type_is_correct():
    transformation = Translation(name="", vector=QVector3D(1, 1, 1))
    assert transformation.type == translation_type


def test_GIVEN_nothing_WHEN_creating_transformation_THEN_transformation_type_is_correct():
    transformation = Transformation(name="")
    assert transformation.type == transform_type
