from geometry_constructor.qml_models.json_model import JsonModel, FilteredJsonModel


def read_json():
    """
    Reads the test data from json files
    :return: a string containing the sample json, and a list of lines for its formatted form
    """
    with open('tests/sample.json', mode='r') as file:
        data = file.read()
    with open('tests/formatted sample.json', mode='r') as file:
        formatted_lines = file.read().splitlines()
    return data, formatted_lines


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
    check_model_contents(model, ['{'])

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
