import logging

import numpy as np

logger = logging.getLogger("NeXus_Constructor_Utils")


def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def is_scalar(object_to_check):
    if hasattr(object_to_check, "__len__"):
        return len(object_to_check) == 1
    return True


def calculate_magnitude(input_vector):
    return np.sqrt(np.sum(np.square(input_vector.astype(float))))


def normalise(input_vector):
    """
    Normalise to unit vector
    :param input_vector: Input vector (numpy array)
    :return: Unit vector, magnitude
    """
    magnitude = calculate_magnitude(input_vector)
    if magnitude == 0:
        return np.array([0.0, 0.0, 0.0]), 0.0
    unit_vector = input_vector.astype(float) / magnitude
    return unit_vector, magnitude


def find_rotation_axis_and_angle_between_vectors(vector_a, vector_b):
    """
    Find the axis and angle of rotation to rotate vector_a onto vector_b
    :param vector_a: 3D vector
    :param vector_b: 3D vector
    :return: axis, angle
    """
    unit_a, mag_a = normalise(vector_a)
    unit_b, mag_b = normalise(vector_b)

    if np.allclose(unit_a, unit_b):
        logger.debug(
            "Vectors coincide; no rotation required in nexusutils.find_rotation_axis_and_angle_between_vectors"
        )
        return None, None

    cross_prod = np.cross(vector_a, vector_b)
    unit_cross, mag_cross = normalise(cross_prod)

    if is_close(mag_cross, 0.0):
        raise NotImplementedError(
            "No unique solution for rotation axis in "
            "nexusutils.find_rotation_axis_and_angle_between_vectors"
        )

    axis = cross_prod / mag_cross
    angle = -1.0 * np.arccos(np.dot(vector_a, vector_b) / (mag_a * mag_b))

    return axis, angle


def find_rotation_matrix_between_vectors(vector_a, vector_b):
    """
    Find the 3D rotation matrix to rotate vector_a onto vector_b
    :param vector_a: 3D vector
    :param vector_b: 3D vector
    :return: 3D rotation matrix
    """
    unit_a, mag_a = normalise(vector_a)
    unit_b, mag_b = normalise(vector_b)
    identity_matrix = np.identity(3)

    if np.allclose(unit_a, unit_b):
        return identity_matrix

    axis, angle = find_rotation_axis_and_angle_between_vectors(vector_a, vector_b)

    skew_symmetric = np.array(
        [
            np.array([0.0, -axis[2], axis[1]]),
            np.array([axis[2], 0.0, -axis[0]]),
            np.array([-axis[1], axis[0], 0.0]),
        ]
    )

    rotation_matrix = (
        identity_matrix
        + np.sin(angle) * skew_symmetric
        + ((1.0 - np.cos(angle)) * (skew_symmetric ** 2.0))
    )
    return rotation_matrix


def parse_off_file(off_file):
    """
    Read vertex list and face definitions from an OFF file and return as lists of numpy arrays
    :param off_file: File object assumed to contain geometry description in OFF format
    :return: List of vertices and list of vertex indices in each face
    """
    file_start = off_file.readline()
    if file_start != "OFF\n":
        logger.error(
            'OFF file is expected to start "OFF", actually started: ' + file_start
        )
        return None
    line = off_file.readline()
    # Skip any comment lines
    while line[0] == "#" or line == "\n":
        line = off_file.readline()
    counts = line.split()
    number_of_vertices = int(counts[0])
    # These values are also in the first line, although we don't need them:
    # number_of_faces = int(counts[1])
    # number_of_edges = int(counts[2])
    off_vertices = np.zeros((number_of_vertices, 3), dtype=float)  # preallocate
    vertex_number = 0
    while vertex_number < number_of_vertices:
        line = off_file.readline()
        if line[0] != "#" and line != "\n":
            off_vertices[vertex_number, :] = np.array(line.split()).astype(float)
            vertex_number += 1

    faces_lines = off_file.readlines()
    # Only keep the first value (number of vertex indices in face) plus the number of vertices.
    # There may be other numbers following it to define a colour for the face, which we don't want to keep
    all_faces = []
    face_colors = []
    for face_line in faces_lines:
        if face_line[0].isdigit():
            face_split = face_line.split()
            idx = int(face_split[0]) + 1
            face = face_split[:idx]
            all_faces.append(np.array(face).astype(int))
            if idx + 3 <= len(face_split):
                color = face_split[idx : idx + 3]
                face_colors.append(np.array(color).astype(int))
            else:
                face_colors.append(np.array([0, 0, 0]).astype(int))
    return off_vertices, all_faces, face_colors


def write_off_file(filename, vertices, faces, winding_order):
    """
    Create an OFF format file
    :param filename: Name for the OFF file to output
    :param vertices: 2D array contains x, y, z coords for each vertex
    :param faces: 1D array indexing into winding_order at the start of each face
    :param winding_order: 1D array of vertex indices in the winding order for each face
    """
    number_of_vertices = len(vertices)
    number_of_faces = len(faces) - 1
    # According to OFF standard the number of edges must be present but does not need to be correct
    number_of_edges = 0
    with open(filename, "wb") as off_file:
        off_file.write("OFF\n".encode("utf8"))
        off_file.write("# NVertices NFaces NEdges\n".encode("utf8"))
        off_file.write(
            "{} {} {}\n".format(
                number_of_vertices, number_of_faces, number_of_edges
            ).encode("utf8")
        )

        off_file.write("# Vertices\n".encode("utf8"))
        np.savetxt(off_file, vertices, fmt="%f", delimiter=" ")

        off_file.write("# Faces\n".encode("utf8"))
        previous_index = 0
        for face in faces[1:]:
            verts_in_face = winding_order[previous_index:face]
            write_off_face(verts_in_face, off_file)
            previous_index = face
        # Last face is the last face index to the end of the winding_order list
        verts_in_face = winding_order[previous_index:]
        write_off_face(verts_in_face, off_file)


def write_off_face(verts_in_face, off_file):
    """
    Write line in the OFF file corresponding to a single face in the geometry
    :param verts_in_face: Indices in the vertex list of the vertices in this face
    :param off_file:  Handle of the file to write to
    """
    fmt_str = "{} " * (len(verts_in_face) + 1)
    fmt_str = fmt_str[:-1] + "\n"
    off_file.write(fmt_str.format(len(verts_in_face), *verts_in_face).encode("utf8"))


def create_off_face_vertex_map(off_faces):
    """
    Avoid having a ragged edge faces dataset due to differing numbers of vertices in faces by recording
    a flattened faces dataset (winding_order) and putting the start index for each face in that
    into the faces dataset.
    :param off_faces: OFF-style faces array, each row is number of vertices followed by vertex indices
    :return: flattened array (winding_order) and the start indices in that (faces)
    """
    faces = []
    winding_order = []
    current_index = 0
    for face in off_faces:
        faces.append(current_index)
        current_index += face[0]
        for vertex_index in face[1:]:
            winding_order.append(vertex_index)
    return np.array(winding_order), np.array(faces)


def construct_cylinder_mesh(height, radius, axis, centre=None, number_of_vertices=50):
    """
    Construct an NXoff_geometry description of a cylinder
    :param height: Height of the tube
    :param radius: Radius of the tube
    :param axis: Axis of the tube as a unit vector
    :param centre: On-axis centre of the tube in form [x, y, z]
    :param number_of_vertices: Maximum number of vertices to use to describe pixel
    :return: vertices and faces (corresponding to OFF description)
    """
    # Construct the geometry as if the tube axis is along x, rotate everything later
    if centre is None:
        centre = [0, 0, 0]
    face_centre = [centre[0] - (height / 2.0), centre[1], centre[2]]
    angles = np.linspace(0, 2 * np.pi, int((number_of_vertices / 2) + 1))
    # The last point is the same as the first so get rid of it
    angles = angles[:-1]
    y = face_centre[1] + radius * np.cos(angles)
    z = face_centre[2] + radius * np.sin(angles)
    num_points_at_each_tube_end = len(y)
    vertices = np.concatenate(
        (
            np.array(list(zip(np.zeros(len(y)) + face_centre[0], y, z))),
            np.array(list(zip(np.ones(len(y)) * height + face_centre[0], y, z))),
        )
    )

    # Rotate vertices to correct the tube axis
    try:
        rotation_matrix = find_rotation_matrix_between_vectors(
            np.array(axis), np.array([1.0, 0.0, 0.0])
        )
    except Exception:
        rotation_matrix = None
    if rotation_matrix is not None:
        vertices = rotation_matrix.dot(vertices.T).T

    #
    # points around left circle tube-end       points around right circle tube-end
    #                                          (these follow the left ones in vertices list)
    #  circular boundary ^                     ^
    #                    |                     |
    #     nth_vertex + 2 .                     . nth_vertex + num_points_at_each_tube_end + 2
    #     nth_vertex + 1 .                     . nth_vertex + num_points_at_each_tube_end + 1
    #     nth_vertex     .                     . nth_vertex + num_points_at_each_tube_end
    #                    |                     |
    #  circular boundary v                     v
    #
    # face starts with the number of vertices in the face (4)
    faces = [
        [
            4,
            nth_vertex,
            nth_vertex + num_points_at_each_tube_end,
            nth_vertex + num_points_at_each_tube_end + 1,
            nth_vertex + 1,
        ]
        for nth_vertex in range(num_points_at_each_tube_end - 1)
    ]
    # Append the last rectangular face
    faces.append(
        [
            4,
            num_points_at_each_tube_end - 1,
            (2 * num_points_at_each_tube_end) - 1,
            num_points_at_each_tube_end,
            0,
        ]
    )
    # NB this is a tube, not a cylinder; I'm not adding the circular faces on the ends of the tube
    faces = np.array(faces)
    return vertices, faces
