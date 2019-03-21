from nexus_constructor.geometry_file_validator import GeometryFileValidator
from PySide2.QtCore import QUrl
from mock import mock_open, patch
import pytest


def test_GIVEN_valid_file_WHEN_validating_OFF_file_THEN_returns_true():
    """ Test that giving a valid OFF file causes the `validate_geometry_file` function to return true. """

    valid_off_file = (
        "OFF\n"
        "#  cube.off\n"
        "#  A cube\n"
        "8 6 0\n"
        "-0.500000 -0.500000 0.500000\n"
        "0.500000 -0.500000 0.500000\n"
        "-0.500000 0.500000 0.500000\n"
        "0.500000 0.500000 0.500000\n"
        "-0.500000 0.500000 -0.500000\n"
        "0.500000 0.500000 -0.500000\n"
        "-0.500000 -0.500000 -0.500000\n"
        "-0.500000 0.500000 0.500000\n"
        "4 0 1 3 2\n"
        "4 2 3 5 4\n"
        "4 4 5 7 6\n"
        "4 6 7 1 0\n"
        "4 1 7 5 3\n"
        "4 6 0 2 4\n"
    )

    with patch("builtins.open", mock_open(read_data=valid_off_file)):
        assert GeometryFileValidator().validate_geometry_file(
            QUrl("mock_valid_file.off")
        )


def test_GIVEN_invalid_file_WHEN_validating_OFF_file_THEN_returns_false():
    """ Test that the `validate_geometry_file` function returns False when given an invalid file. """

    invalid_off_files = [
        # Empty file
        "",
        (  # File missing a point
            "OFF\n"
            "#  cube.off\n"
            "#  A cube\n"
            "8 6 0\n"
            "-0.500000 -0.500000 0.500000\n"
            "0.500000 -0.500000 0.500000\n"
            "-0.500000 0.500000 0.500000\n"
            "0.500000 0.500000 0.500000\n"
            "-0.500000 0.500000 -0.500000\n"
            "0.500000 0.500000 -0.500000\n"
            "-0.500000 -0.500000 -0.500000\n"
            "4 0 1 3 2\n"
            "4 2 3 5 4\n"
            "4 4 5 7 6\n"
            "4 6 7 1 0\n"
            "4 1 7 5 3\n"
            "4 6 0 2 4\n"
        ),
        (  # File with text in place of a z-coordinate
            "OFF\n"
            "#  cube.off\n"
            "#  A cube\n"
            "8 6 0\n"
            "-0.500000 -0.500000 0.500000\n"
            "0.500000 -0.500000 0.500000\n"
            "-0.500000 0.500000 0.500000\n"
            "0.500000 0.500000 0.500000\n"
            "-0.500000 0.500000 -0.500000\n"
            "0.500000 0.500000 -0.500000\n"
            "-0.500000 -0.500000 aaaaa\n"
            "0.500000 -0.500000 -0.500000\n"
            "4 0 1 3 2\n"
            "4 2 3 5 4\n"
            "4 4 5 7 6\n"
            "4 6 7 1 0\n"
            "4 1 7 5 3\n"
            "4 6 0 2 4\n"
        ),
        (  # File with a missing z-coordinate
            "OFF\n"
            "#  cube.off\n"
            "#  A cube\n"
            "8 6 0\n"
            "-0.500000 -0.500000 0.500000\n"
            "0.500000 -0.500000 0.500000\n"
            "-0.500000 0.500000 0.500000\n"
            "0.500000 0.500000 0.500000\n"
            "-0.500000 0.500000 -0.500000\n"
            "0.500000 0.500000 -0.500000\n"
            "-0.500000 -0.500000\n"
            "0.500000 -0.500000 -0.500000\n"
            "4 0 1 3 2\n"
            "4 2 3 5 4\n"
            "4 4 5 7 6\n"
            "4 6 7 1 0\n"
            "4 1 7 5 3\n"
            "4 6 0 2 4\n"
        ),
        "OFF\n#  cube.off\n#  A cube\n",  # File with no points
        (  # File that doesn't start with "OFF"
            "#  cube.off\n"
            "#  A cube\n"
            "8 6 0\n"
            "-0.500000 -0.500000 0.500000\n"
            "0.500000 -0.500000 0.500000\n"
            "-0.500000 0.500000 0.500000\n"
            "0.500000 0.500000 0.500000\n"
            "-0.500000 0.500000 -0.500000\n"
            "0.500000 0.500000 -0.500000\n"
            "-0.500000 -0.500000 -0.500000\n"
            "0.500000 -0.500000 -0.500000\n"
            "4 0 1 3 2\n"
            "4 2 3 5 4\n"
            "4 4 5 7 6\n"
            "4 6 7 1 0\n"
            "4 1 7 5 3\n"
            "4 6 0 2 4\n"
        ),
    ]

    for invalid_off_file in invalid_off_files:
        with patch("builtins.open", mock_open(read_data=invalid_off_file)):
            assert not GeometryFileValidator().validate_geometry_file(
                QUrl("mock_invalid_file.off")
            )


def test_GIVEN_valid_file_WHEN_validating_STL_file_THEN_returns_true():

    valid_stl_file = (
        "solid dart\n"
        "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
        "outer loop\n"
        "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
        "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
        "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
        "endloop\n"
        "endfacet\n"
        "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
        "outer loop\n"
        "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
        "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
        "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
        "endloop\n"
        "endfacet\n"
        "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
        "outer loop\n"
        "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
        "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
        "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
        "endloop\n"
        "endfacet\n"
        "endsolid dart\n"
    )

    with patch("builtins.open", mock_open(read_data=valid_stl_file)):
        assert GeometryFileValidator().validate_geometry_file(
            QUrl("mock_valid_file.stl")
        )


@pytest.mark.skip()
def test_GIVEN_invalid_file_WHEN_validating_STL_file_THEN_returns_false():
    """ Test that the `validate_geometry_file` function returns False when given an invalid STL file. """

    invalid_stl_files = [
        # Empty file
        "",
        # Gibberish
        "abcd",
        (  # File with missing endloop statement
            "solid dart\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "endfacet\n"
            "endsolid dart\n"
        ),
        (  # File with missing end solid statement
            "solid dart\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
        ),
        (  # File with missing vertex
            "solid dart\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "endsolid dart\n"
        ),
        (  # File with empty vertex
            "solid dart\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
            "vertex\n"
            "endloop\n"
            "endfacet\n"
            "endsolid dart\n"
        ),
        (  # Vertex missing a coordinate
            "solid dart\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001\n"
            "endloop\n"
            "endfacet\n"
            "endsolid dart\n"
        ),
        (  # Empty loop
            "solid dart\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
            "outer loop\n"
            "endloop\n"
            "endfacet\n"
            "endsolid dart\n"
        ),
        (  # Vertex that contains characters
            "solid dart\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex aaa 4.15500E+001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "endsolid dart\n"
        ),
        (  # Incorrect keyword
            "solid dart\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "verrrrtex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "endsolid dart\n"
        ),
        (  # endloop in wrong place
            "solid dart\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "endloop\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
            "outer loop\n"
            "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
            "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
            "endloop\n"
            "endfacet\n"
            "endsolid dart\n"
        ),
    ]

    for invalid_stl_file in invalid_stl_files:
        with patch("builtins.open", mock_open(read_data=invalid_stl_file)):
            assert not GeometryFileValidator().validate_geometry_file(
                QUrl("mock_valid_file.stl")
            )
