from geometry_constructor.qml_json_model import JsonModel, FilteredJsonModel


def read_json():
    """
    Reads the test data from json files
    :return: a string containing the pretty printed json, and a list of lines for its condensed form
    """
    with open('tests/pretty printed sample.json', mode='r') as file:
        data = file.read()
    with open('tests/condensed sample.json', mode='r') as file:
        condensed_lines = file.read().splitlines()
    return data, condensed_lines


def read_collapsed_data():
    """
    Reads the expected collapsed lines for a model based on the sample json data
    :return: a list of strings containing the collapsed lines
    """
    with open('tests/collapsed lines.txt') as file:
        return file.read().splitlines()


def check_model_contents(model, expected_values, role=JsonModel.TextRole):
    """Tests that the objects in a model have expected values for a given property"""
    assert model.rowCount() == len(expected_values)
    for i in range(model.rowCount()):
        index = model.index(i, 0)
        assert model.data(index, role) == expected_values[i]


def test_initialise_json_model():
    """Tests that the json model class initialises and loads data correctly"""
    data, condensed_lines = read_json()
    collapsed_lines = read_collapsed_data()

    model = JsonModel()
    model.set_json(data)

    check_model_contents(model, condensed_lines)
    check_model_contents(model, collapsed_lines, JsonModel.CollapsedTextRole)


def test_initialise_filtered_json_model():
    """Tests that the filtered json model class initialises and loads data correctly"""
    data, condensed_lines = read_json()
    collapsed_lines = read_collapsed_data()

    model = FilteredJsonModel()
    model.set_json(data)

    check_model_contents(model, condensed_lines)
    check_model_contents(model, collapsed_lines, JsonModel.CollapsedTextRole)


def test_collapse_model_root():
    """Tests that collapsing the root object hides all other lines in the model"""
    data, condensed_lines = read_json()

    model = FilteredJsonModel()
    model.set_json(data)

    starting_index = model.index(0, 0)

    # Collapse the first item in the model, the objects opening bracket, filtering out all other items
    model.setData(starting_index, True, JsonModel.CollapsedRole)
    check_model_contents(model, ['{'])

    # Un-collapse it, restoring the other items
    model.setData(starting_index, False, JsonModel.CollapsedRole)
    check_model_contents(model, condensed_lines)


def test_collapse_condensed_list():
    """Tests that collapsing a list that's condensed onto a single line won't hide any lines in the model"""
    data, condensed_lines = read_json()

    model = FilteredJsonModel()
    model.set_json(data)

    model.setData(model.index(39, 0), True, JsonModel.CollapsedRole)
    check_model_contents(model, condensed_lines)
    model.setData(model.index(39, 0), False, JsonModel.CollapsedRole)
    check_model_contents(model, condensed_lines)


def test_collapse_nested_object():
    """Tests that collapsing an object within the json hides the correct lines in the model"""
    data, condensed_lines = read_json()

    model = FilteredJsonModel()
    model.set_json(data)

    model.setData(model.index(1, 0), True, JsonModel.CollapsedRole)
    visible_lines = condensed_lines[:2] + condensed_lines[45:]
    check_model_contents(model, visible_lines)

    model.setData(model.index(1, 0), False, JsonModel.CollapsedRole)
    check_model_contents(model, condensed_lines)


def test_collapse_list_items():
    """Tests that collapsing and re-expanding objects in a list hides and then restores the correct lines"""
    data, condensed_lines = read_json()

    model = FilteredJsonModel()
    model.set_json(data)

    # Collapse the first transform
    model.setData(model.index(3, 0), True, JsonModel.CollapsedRole)
    visible_lines = condensed_lines[:4] + condensed_lines[15:]
    check_model_contents(model, visible_lines)
    # Un-collapse the first transform
    model.setData(model.index(3, 0), False, JsonModel.CollapsedRole)
    check_model_contents(model, condensed_lines)

    # Collapse the second transform
    model.setData(model.index(15, 0), True, JsonModel.CollapsedRole)
    visible_lines = condensed_lines[:16] + condensed_lines[24:]
    check_model_contents(model, visible_lines)
    # Un-collapse the second transform
    model.setData(model.index(15, 0), False, JsonModel.CollapsedRole)
    check_model_contents(model, condensed_lines)
