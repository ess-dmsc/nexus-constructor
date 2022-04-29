import logging
from typing import BinaryIO, TextIO, Union

from PySide2.QtGui import QVector3D
from stl import mesh

from nexus_constructor.model.geometry import OFFGeometry, OFFGeometryNoNexus
from nexus_constructor.unit_utils import METRES, calculate_unit_conversion_factor
from nexus_constructor.utils.readwriteoff import parse_off_file


def load_geometry(
    filename: str, units: str, geometry: OFFGeometryNoNexus = OFFGeometryNoNexus()
) -> OFFGeometry:
    """
    Loads geometry from a file into an OFFGeometry instance

    Supported file types are OFF and STL.
    :param filename: The name of the file to open.
    :param units: A unit of length in the form of a string. Used to determine the multiplication factor.
    :param geometry: The optional OFFGeometry to load the geometry data into. If not provided, a new instance will be
    returned.
    :return: An OFFGeometry instance containing that file's geometry, or an empty instance if filename's extension is
    unsupported.
    """

    extension = filename[filename.rfind(".") :].lower()

    try:
        with open(filename) as file:
            return load_geometry_from_file_object(file, extension, units, geometry)
    except UnicodeDecodeError:
        # Try again in case the file is in binary. At least one of these should work when a user selects a file because
        # GeometryFileValidator inspects the file beforehand to check that it's valid.
        with open(filename, "rb") as file_bin:
            return load_geometry_from_file_object(file_bin, extension, units, geometry)


def load_geometry_from_file_object(
    file: Union[BinaryIO, TextIO],
    extension: str,
    units: str,
    geometry: OFFGeometryNoNexus = OFFGeometryNoNexus(),
) -> OFFGeometry:
    """
    Loads geometry from a file object into an OFFGeometry instance

    Supported file types are OFF and STL.

    :param file: The file object to load the geometry from.
    :param units: A unit of length in the form of a string. Used to determine the multiplication factor.
    :param geometry: The optional OFFGeometry to load the geometry data into. If not provided, a new instance will be
    returned.
    :return: An OFFGeometry instance containing that file's geometry, or an empty instance if filename's extension is
    unsupported.
    """

    mult_factor = calculate_unit_conversion_factor(units, METRES)

    if extension == ".off":
        _load_off_geometry(file, mult_factor, geometry)
    elif extension == ".stl":
        _load_stl_geometry(file, mult_factor, geometry)
    else:
        geometry.faces = []
        geometry.vertices = []
        logging.error("geometry file extension not supported")

    return geometry


def _load_off_geometry(
    file: Union[BinaryIO, TextIO],
    mult_factor: float,
    geometry: OFFGeometryNoNexus = OFFGeometryNoNexus(),
) -> OFFGeometry:
    """
    Loads geometry from an OFF file into an OFFGeometry instance.

    :param file: The file containing an OFF geometry.
    :param mult_factor: The multiplication factor for unit conversion.
    :param geometry: The optional OFFGeometry to load the OFF data into. If not provided, a new instance will be
    returned.
    :return: An OFFGeometry instance containing that file's geometry.
    """
    vertices, faces = parse_off_file(file)

    geometry.vertices = [
        QVector3D(x * mult_factor, y * mult_factor, z * mult_factor)
        for x, y, z in (vertex for vertex in vertices)
    ]
    geometry.faces = [face.tolist()[1:] for face in faces]
    logging.info("OFF loaded")
    return geometry


def _load_stl_geometry(
    file: Union[BinaryIO, TextIO],
    mult_factor: float,
    geometry: OFFGeometryNoNexus = OFFGeometryNoNexus(),
) -> OFFGeometry:
    """
    Loads geometry from an STL file into an OFFGeometry instance.

    :param file: The file containing an STL geometry.
    :param mult_factor: The multiplication factor for unit conversion.
    :param geometry: The optional OFFGeometry to load the STL data into. If not provided, a new instance will be
    returned.
    :return: An OFFGeometry instance containing that file's geometry.
    """
    mesh_data = mesh.Mesh.from_file("", fh=file, calculate_normals=False)
    # numpy-stl loads numbers as python decimals, not floats, which aren't valid in json
    geometry.vertices = [
        QVector3D(
            float(corner[0]) * mult_factor,
            float(corner[1]) * mult_factor,
            float(corner[2]) * mult_factor,
        )
        for triangle in mesh_data.vectors
        for corner in triangle
    ]
    geometry.faces = [
        [i * 3, (i * 3) + 1, (i * 3) + 2] for i in range(len(mesh_data.vectors))
    ]
    logging.info("STL loaded")
    return geometry
