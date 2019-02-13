from nexus_constructor.data_model import OFFGeometry, Vector
from nexusutils.readwriteoff import parse_off_file
from stl import mesh
import pint

def load_geometry(filename: str, geometry: OFFGeometry=OFFGeometry()):
    """
    Loads geometry from a file into an OFFGeometry instance

    Supported file types are OFF and STL.
    :param filename: The name of the file to load geometry from
    :param geometry: The optional OFFGeometry to load the geometry data into. If not provided, a new instance will be
    returned
    :return: An OFFGeometry instance containing that file's geometry, or an empty instance if filename's extension is
    unsupported
    """
    extension = filename[filename.rfind('.'):].lower()
    if extension == '.off':
        load_off_geometry(filename, geometry)
    elif extension == '.stl':
        load_stl_geometry(filename, geometry)
    else:
        geometry.faces = []
        geometry.vertices = []
        print('geometry file extension not supported')
    return geometry


def load_off_geometry(filename: str, geometry: OFFGeometry=OFFGeometry()):
    """
    Loads geometry from an OFF file into an OFFGeometry instance

    :param filename: The name of the OFF file to load geometry from
    :param geometry: The optional OFFGeometry to load the OFF data into. If not provided, a new instance will be
    returned
    :return: An OFFGeometry instance containing that file's geometry
    """
    with open(filename) as file:
        vertices, faces = parse_off_file(file)

    geometry.vertices = [Vector(x, y, z) for x, y, z in (vertex for vertex in vertices)]
    geometry.faces = [face.tolist()[1:] for face in faces]
    print('OFF loaded')
    return geometry


def load_stl_geometry(filename: str, geometry: OFFGeometry=OFFGeometry()):
    """
    Loads geometry from an STL file into an OFFGeometry instance

    :param filename: The name of the STL file to load geometry from
    :param geometry: The optional OFFGeometry to load the STL data into. If not provided, a new instance will be
    returned
    :return: An OFFGeometry instance containing that file's geometry
    """
    mesh_data = mesh.Mesh.from_file(filename, calculate_normals=False)
    # numpy-stl loads numbers as python decimals, not floats, which aren't valid in json
    geometry.vertices = [Vector(float(corner[0]),
                                float(corner[1]),
                                float(corner[2]))
                         for triangle in mesh_data.vectors
                         for corner in triangle]
    geometry.faces = [[i * 3, (i * 3) + 1, (i * 3) + 2] for i in range(len(mesh_data.vectors))]
    print('STL loaded')
    return geometry


def is_length(str):
    """
    Checks that a string argument is a unit of length.

    :param str: A unit in the form of a string
    :return: True if the string is a unit of length and false if it is not.
    """
    ureg = pint.UnitRegistry()

    try:
        unit = ureg(str)
    except pint.errors.UndefinedUnitError:
        return False

    return unit.dimensionality['[length]'] == 1.0
