import pytest
from PySide2.QtGui import QVector3D
from pytest import approx

from nexus_constructor.geometry.utils import (
    get_an_orthogonal_unit_vector,
    validate_nonzero_qvector,
)


def test_zero_qvector_raises_error_when_validated():
    test_vector = QVector3D(0, 0, 0)
    assert validate_nonzero_qvector(test_vector)


@pytest.mark.parametrize(
    "nonzero_input_vector",
    [(QVector3D(1, 0, 0),), (QVector3D(2, 3, 8),), (QVector3D(0, -1, 0),)],
)
def test_non_zero_qvector_does_not_raise_error_when_validated(nonzero_input_vector):
    assert not validate_nonzero_qvector(nonzero_input_vector[0])


@pytest.mark.parametrize(
    "test_vector",
    [(QVector3D(1, 0, 0),), (QVector3D(2, 3, -8),), (QVector3D(0, -1, 0),)],
)
def test_get_an_orthogonal_unit_vector_gives_a_unit_vector(test_vector):
    result_vector = get_an_orthogonal_unit_vector(test_vector[0])
    assert result_vector.length() == approx(1)


@pytest.mark.parametrize(
    "test_vector",
    [
        (QVector3D(1, 0, 0),),
        (QVector3D(0, 1, 0),),
        (QVector3D(0, 0, 1),),
        (QVector3D(2, 3, -8),),
        (QVector3D(0, -1, 0),),
        (QVector3D(0.1, -1, 0),),
    ],
)
def test_get_an_orthogonal_unit_vector_gives_an_orthogonal_vector(test_vector):
    result_vector = get_an_orthogonal_unit_vector(test_vector[0])
    # Test orthogonal (dot product is zero)
    assert QVector3D.dotProduct(test_vector[0], result_vector) == approx(0)
