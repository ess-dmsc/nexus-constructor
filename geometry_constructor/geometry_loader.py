from geometry_constructor.data_model import OFFGeometry, Vector
from nexusutils.readwriteoff import parse_off_file
from stl import mesh


def load_geometry(filename: str):
    """
    Loads geometry from a file into an OFFGeometry instance

    Supported file types are OFF and STL.
    :param filename: The name of the file to load geometry from
    :return: An OFFGeometry instance containing that file's geometry, or an empty instance if filename's extension is
    unsupported
    """
    extension = filename[filename.rfind('.'):].lower()
    if extension == '.off':
        return load_off_geometry(filename)
    elif extension == '.stl':
        return load_stl_geometry(filename)
    else:
        print('geometry file extension not supported')
        return OFFGeometry()


def load_off_geometry(filename: str):
    """
    Loads geometry from an OFF file into an OFFGeometry instance

    :param filename: The name of the OFF file to load geometry from
    :return: An OFFGeometry instance containing that file's geometry
    """
    with open(filename) as file:
        vertices, faces = parse_off_file(file)

    vertices = [Vector(x, y, z) for x, y, z in (vertex for vertex in vertices)]
    faces = [face.tolist()[1:] for face in faces]
    print('OFF loaded')
    return OFFGeometry(vertices=vertices, faces=faces)


def load_stl_geometry(filename: str):
    """
    Loads geometry from an STL file into an OFFGeometry instance

    :param filename: The name of the STL file to load geometry from
    :return: An OFFGeometry instance containing that file's geometry
    """
    mesh_data = mesh.Mesh.from_file(filename, calculate_normals=False)
    # numpy-stl loads numbers as python decimals, not floats, which aren't valid in json
    vertices = [Vector(float(corner[0]),
                       float(corner[1]),
                       float(corner[2]))
                for triangle in mesh_data.vectors
                for corner in triangle]
    faces = [[i * 3, (i * 3) + 1, (i * 3) + 2] for i in range(len(mesh_data.vectors))]
    print('STL loaded')
    return OFFGeometry(vertices=vertices, faces=faces)
