import pytest

from nexus_constructor.model.node import FieldAttribute
import numpy as np

NAME = "field1"


def test_attribute_with_equal_numpy_arrays_as_values_are_equal():
    a = FieldAttribute(name=NAME, values=np.array([1, 2, 3, 4, 5]))
    b = FieldAttribute(name=NAME, values=np.array([1, 2, 3, 4, 5]))
    assert a == b


def test_attributes_with_equal_numpy_scalars_are_equal():
    a = FieldAttribute(name=NAME, values=np.int32(1))
    b = FieldAttribute(name=NAME, values=np.int32(1))
    assert a == b


@pytest.mark.parametrize("test_input", [1, "test", 1.0, [1, 2, 3]])
def test_attributes_with_equal_python_types_are_equal(test_input):
    a = FieldAttribute(name=NAME, values=test_input)
    b = FieldAttribute(name=NAME, values=test_input)
    assert a == b


def test_attributes_with_None_as_values_are_equal():
    a = FieldAttribute(name=NAME, values=None)
    b = FieldAttribute(name=NAME, values=None)

    assert a == b


def test_attributes_with_unequal_numpy_arrays_as_values_are_unequal():
    a = FieldAttribute(name=NAME, values=np.array([2, 2, 3, 4, 5]))
    b = FieldAttribute(name=NAME, values=np.array([1, 2, 3, 4, 5]))
    assert a != b


def test_attributes_with_unequal_numpy_scalars_are_unequal():
    a = FieldAttribute(name=NAME, values=np.int32(2))
    b = FieldAttribute(name=NAME, values=np.int32(1))
    assert a != b


@pytest.mark.parametrize("test_input", [1, "test", 1.0, True, [1, 2, 3]])
def test_attributes_with_unequal_python_values_are_unequal(test_input):
    a = FieldAttribute(name=NAME, values=test_input)
    b = FieldAttribute(name=NAME, values="something different")
    assert a != b


def test_attributes_with_different_names_but_same_value_are_unequal():
    a = FieldAttribute(name=NAME, values=1)
    b = FieldAttribute(name="field2", values=1)
    assert a != b
