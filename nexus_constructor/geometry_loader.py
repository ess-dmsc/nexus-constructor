from nexus_constructor.data_model import OFFGeometry
from nexusutils.readwriteoff import parse_off_file
from nexus_constructor.unit_converter import calculate_unit_conversion_factor
from stl import mesh
from PySide2.QtGui import QVector3D


def load_geometry(filename: str, units: str, geometry: OFFGeometry = OFFGeometry()):
    """
    Loads geometry from a file into an OFFGeometry instance

    Supported file types are OFF and STL.
    :param filename: The name of the file to load geometry from
    :param str: A unit of length in the form of a string. Used to determine the multiplication factor.
    :param geometry: The optional OFFGeometry to load the geometry data into. If not provided, a new instance will be
    returned
    :return: An OFFGeometry instance containing that file's geometry, or an empty instance if filename's extension is
    unsupported
    """
    mult_factor = calculate_unit_conversion_factor(units)

    extension = filename[filename.rfind(".") :].lower()
    if extension == ".off":
        load_off_geometry(filename, mult_factor, geometry)
    elif extension == ".stl":
        load_stl_geometry(filename, mult_factor, geometry)
    else:
        geometry.faces = []
        geometry.vertices = []
        print("geometry file extension not supported")
    return geometry


def load_off_geometry(
    filename: str, mult_factor: float, geometry: OFFGeometry = OFFGeometry()
):
    """
    Loads geometry from an OFF file into an OFFGeometry instance

    :param filename: The name of the OFF file to load geometry from
    :param mult_factor: The multiplication factor for unit conversion
    :param geometry: The optional OFFGeometry to load the OFF data into. If not provided, a new instance will be
    returned
    :return: An OFFGeometry instance containing that file's geometry
    """
    with open(filename) as file:
        try:
            vertices, faces = parse_off_file(file)
        except (ValueError, TypeError):
            # File is empty or invalid
            return False

    geometry.vertices = [
        QVector3D(x * mult_factor, y * mult_factor, z * mult_factor)
        for x, y, z in (vertex for vertex in vertices)
    ]
    geometry.faces = [face.tolist()[1:] for face in faces]
    print("OFF loaded")
    return geometry


def load_stl_geometry(
    filename: str, mult_factor: float, geometry: OFFGeometry = OFFGeometry()
):
    """
    Loads geometry from an STL file into an OFFGeometry instance

    :param filename: The name of the STL file to load geometry from
    :param mult_factor: The multiplication factor for unit conversion
    :param geometry: The optional OFFGeometry to load the STL data into. If not provided, a new instance will be
    returned
    :return: An OFFGeometry instance containing that file's geometry
    """
    mesh_data = mesh.Mesh.from_file(filename, calculate_normals=False)
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
    print("STL loaded")
    return geometry
