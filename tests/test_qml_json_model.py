from nexus_constructor.qml_models.json_model import JsonModel, FilteredJsonModel
from io import StringIO


def read_json():
    """
    Reads the test data from json files
    :return: a string containing the sample json, and a list of lines for its formatted form
    """
    sample = (
        "{\n"
        '"sample": {\n'
        '"transforms": [\n'
        "{\n"
        '"angle": {\n'
        '"unit": "degrees",\n'
        '"value": 0\n'
        "},\n"
        '"axis": {\n'
        '"y": 0,\n'
        '"z": 1,\n'
        '"x": 0\n'
        "},\n"
        '"type": "rotate"\n'
        "},\n"
        "{\n"
        '"unit": "m",\n'
        '"vector": {\n'
        '"y": 0,\n'
        '"z": 0,\n'
        '"x": 0\n'
        "},\n"
        '"type": "translate"\n'
        "}\n"
        "],\n"
        '"transform_id": 0,\n'
        '"name": "Sample",\n'
        '"description": "",\n'
        '"geometry": {\n'
        '"vertices": [\n'
        "[\n"
        "-0.5,\n"
        "-0.5,\n"
        "0.5\n"
        "],\n"
        "[\n"
        "0.5,\n"
        "-0.5,\n"
        "0.5\n"
        "],\n"
        "[\n"
        "-0.5,\n"
        "0.5,\n"
        "0.5\n"
        "],\n"
        "[\n"
        "0.5,\n"
        "0.5,\n"
        "0.5\n"
        "],\n"
        "[\n"
        "-0.5,\n"
        "0.5,\n"
        "-0.5\n"
        "],\n"
        "[\n"
        "0.5,\n"
        "0.5,\n"
        "-0.5\n"
        "],\n"
        "[\n"
        "-0.5,\n"
        "-0.5,\n"
        "-0.5\n"
        "],\n"
        "[\n"
        "0.5,\n"
        "-0.5,\n"
        "-0.5\n"
        "]\n"
        "],\n"
        '"faces": [\n'
        "0,\n"
        "1,\n"
        "3,\n"
        "2,\n"
        "2,\n"
        "3,\n"
        "5,\n"
        "4,\n"
        "4,\n"
        "5,\n"
        "7,\n"
        "6,\n"
        "6,\n"
        "7,\n"
        "1,\n"
        "0,\n"
        "1,\n"
        "7,\n"
        "5,\n"
        "3,\n"
        "6,\n"
        "0,\n"
        "2,\n"
        "4\n"
        "],\n"
        '"winding_order": [\n'
        "0,\n"
        "4,\n"
        "8,\n"
        "12,\n"
        "16,\n"
        "20\n"
        "],\n"
        '"type": "OFF"\n'
        "},\n"
        '"type": "Sample"\n'
        "},\n"
        '"components": []\n'
        "}\n"
    )

    data = StringIO(sample).read()

    # The spaces are needed for the tests to pass
    formatted_sample = (
        """{
           "components": [],
           "sample": {
             "description": "",
            "geometry": {
              "faces": [0, 1, 3, 2, 2, 3, 5, 4, 4, 5, 7, 6, 6, 7, 1, 0, 1, 7, 5, 3, 6, 0, 2, 4],
              "type": "OFF",
              "vertices": [
                [-0.5, -0.5, 0.5],
                [0.5, -0.5, 0.5],
                [-0.5, 0.5, 0.5],
                [0.5, 0.5, 0.5],
                [-0.5, 0.5, -0.5],
                [0.5, 0.5, -0.5],
                [-0.5, -0.5, -0.5],
                [0.5, -0.5, -0.5]
              ],
              "winding_order": [0, 4, 8, 12, 16, 20]
            },
            "name": "Sample",
            "transform_id": 0,
            "transforms": [
              {
                "angle": {
                  "unit": "degrees",
                  "value": 0
                },
                "axis": {
                  "x": 0,
                  "y": 0,
                  "z": 1
                },
                "type": "rotate"
              },
              {
                "type": "translate",
                "unit": "m",
                "vector": {
                  "x": 0,
                  "y": 0,
                  "z": 0
                }
              }
            ],
            "type": "Sample"
          }
        }"""
    )

    formatted_lines = StringIO(formatted_sample).read().splitlines()

    return data, formatted_lines


def read_collapsed_data():
    """
    Reads the expected collapsed lines for a model based on the sample json data
    :return: a list of strings containing the collapsed lines
    """

    # The spaces are needed for the tests to pass
    collapsed_lines = (
        "{...}\n"
        '  "components": [],\n'
        '  "sample": {...}\n'
        '    "description": "",\n'
        '    "geometry": {...},\n'
        '      "faces": [...],\n'
        '      "type": "OFF",\n'
        '      "vertices": [...],\n'
        "        [...],\n"
        "        [...],\n"
        "        [...],\n"
        "        [...],\n"
        "        [...],\n"
        "        [...],\n"
        "        [...],\n"
        "        [...]\n"
        "      ],\n"
        '      "winding_order": [...]\n'
        "    },\n"
        '    "name": "Sample",\n'
        '    "transform_id": 0,\n'
        '    "transforms": [...],\n'
        "      {...},\n"
        '        "angle": {...},\n'
        '          "unit": "degrees",\n'
        '          "value": 0\n'
        "        },\n"
        '        "axis": {...},\n'
        '          "x": 0,\n'
        '          "y": 0,\n'
        '          "z": 1\n'
        "        },\n"
        '        "type": "rotate"\n'
        "      },\n"
        "      {...}\n"
        '        "type": "translate",\n'
        '        "unit": "m",\n'
        '        "vector": {...}\n'
        '          "x": 0,\n'
        '          "y": 0,\n'
        '          "z": 0\n'
        "        }\n"
        "      }\n"
        "    ],\n"
        '    "type": "Sample"\n'
        "  }\n"
        "}\n"
    )

    return StringIO(collapsed_lines).read().splitlines()


def check_model_contents(model, expected_values, role=JsonModel.TextRole):
    """Tests that the objects in a model have expected values for a given property"""
    assert model.rowCount() == len(expected_values)
    for i in range(model.rowCount()):
        index = model.index(i, 0)
        assert model.data(index, role).strip() == expected_values[i].strip()


def test_initialise_json_model():
    """Tests that the json model class initialises and loads data correctly"""
    data, formatted_lines = read_json()
    collapsed_lines = read_collapsed_data()

    model = JsonModel()
    model.set_json(data)

    check_model_contents(model, formatted_lines)
    check_model_contents(model, collapsed_lines, JsonModel.CollapsedTextRole)


def test_initialise_filtered_json_model():
    """Tests that the filtered json model class initialises and loads data correctly"""
    data, formatted_lines = read_json()
    collapsed_lines = read_collapsed_data()

    model = FilteredJsonModel()
    model.set_json(data)

    check_model_contents(model, formatted_lines)
    check_model_contents(model, collapsed_lines, JsonModel.CollapsedTextRole)


def test_collapse_model_root():
    """Tests that collapsing the root object hides all other lines in the model"""
    data, formatted_lines = read_json()

    model = FilteredJsonModel()
    model.set_json(data)

    starting_index = model.index(0, 0)

    # Collapse the first item in the model, the objects opening bracket, filtering out all other items
    model.setData(starting_index, True, JsonModel.CollapsedRole)
    check_model_contents(model, ["{"])

    # Un-collapse it, restoring the other items
    model.setData(starting_index, False, JsonModel.CollapsedRole)
    check_model_contents(model, formatted_lines)


def test_collapse_condensed_list():
    """Tests that collapsing a list that's condensed onto a single line won't hide any lines in the model"""
    data, formatted_lines = read_json()

    model = FilteredJsonModel()
    model.set_json(data)

    model.setData(model.index(39, 0), True, JsonModel.CollapsedRole)
    check_model_contents(model, formatted_lines)
    model.setData(model.index(39, 0), False, JsonModel.CollapsedRole)
    check_model_contents(model, formatted_lines)


def test_collapse_nested_object():
    """Tests that collapsing an object within the json hides the correct lines in the model"""
    data, formatted_lines = read_json()

    model = FilteredJsonModel()
    model.set_json(data)

    model.setData(model.index(2, 0), True, JsonModel.CollapsedRole)
    visible_lines = formatted_lines[:3] + formatted_lines[46:]
    check_model_contents(model, visible_lines)

    model.setData(model.index(2, 0), False, JsonModel.CollapsedRole)
    check_model_contents(model, formatted_lines)


def test_collapse_list_items():
    """Tests that collapsing and re-expanding objects in a list hides and then restores the correct lines"""
    data, formatted_lines = read_json()

    model = FilteredJsonModel()
    model.set_json(data)

    # Collapse the first transform
    model.setData(model.index(22, 0), True, JsonModel.CollapsedRole)
    visible_lines = formatted_lines[:23] + formatted_lines[34:]
    check_model_contents(model, visible_lines)
    # Un-collapse the first transform
    model.setData(model.index(22, 0), False, JsonModel.CollapsedRole)
    check_model_contents(model, formatted_lines)

    # Collapse the second transform
    model.setData(model.index(34, 0), True, JsonModel.CollapsedRole)
    visible_lines = formatted_lines[:35] + formatted_lines[43:]
    check_model_contents(model, visible_lines)
    # Un-collapse the second transform
    model.setData(model.index(34, 0), False, JsonModel.CollapsedRole)
    check_model_contents(model, formatted_lines)
