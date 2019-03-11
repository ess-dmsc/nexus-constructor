from nexus_constructor.transformation import Rotation, Translation, Vector


def test_GIVEN_name_WHEN_creating_transformation_THEN_name_appears_in_nexus_attribute():
    name = "test"
    transformation = Rotation(0, name)
    assert transformation.name == name


def test_GIVEN_angle_WHEN_creating_rotation_THEN_angle_is_set_correctly():
    angle = 180
    transformation = Rotation(angle, name="name")
    assert transformation.angle == angle


def test_GIVEN_axis_WHEN_creating_rotation_THEN_axis_is_set_correctly():
    axis = Vector(1, 0, 0)
    transformation = Rotation(0, axis=axis, name="name")
    assert transformation.axis.xyz_list == axis.xyz_list


def test_GIVEN_name_WHEN_creating_rotation_THEN_group_and_class_is_created_correctly():

    name = "name"
    transformation = Rotation(0, axis=Vector(1, 0, 0), name=name)
    dataset = transformation.nexus_file.get(name)
    assert dataset.name[1:] == name
    assert dataset.attrs["NX_class"] == "NXtransformations"


def test_GIVEN_name_WHEN_creating_translation_THEN_group_and_class_is_created_correctly():

    name = "name"
    transformation = Translation(vector=Vector(1, 0, 0), name=name)
    dataset = transformation.nexus_file.get(name)
    assert dataset.name[1:] == name
    assert dataset.attrs["NX_class"] == "NXtransformations"


def test_GIVEN_vector_WHEN_creating_translation_THEN_translation_is_set_correctly():

    vector = Vector(1, 1, 1)
    transformation = Translation(vector=vector, name="name")
    assert transformation.vector.xyz_list == vector.xyz_list


def test_GIVEN_nothing_WHEN_creating_rotation_THEN_transfomation_type_is_correct():

    name = "name"
    transformation = Rotation(0, name, Vector(1, 0, 0))
    transformation.nexus_file.get(name).attrs["transformation_type"] == "rotation"


def test_GIVEN_nothing_WHEN_creating_translation_THEN_transformation_type_is_correct():

    name = "name"
    transformation = Translation(name, Vector(1, 1, 1))
    transformation.nexus_file.get(name).attrs["transformation_type"] == "translation"


def test_GIVEN_vector_WHEN_creating_translation_THEN_vector_attribute_is_correct():

    name = "name"
    vector = Vector(1, 1, 1)
    transformation = Translation(name, vector)
    transformation.nexus_file.get(name).attrs["vector"] == vector.xyz_list
