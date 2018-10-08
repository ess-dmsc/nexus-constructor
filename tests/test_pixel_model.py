from geometry_constructor import Models


def test_initialise_model():
    model = Models.InstrumentModel()
    assert model.rowCount() == 1


def test_add_component():
    model = Models.InstrumentModel()
    model.add_detector("My Detector")
    assert model.rowCount() == 2
    assert model.components[1] == Models.Detector(name="My Detector")
    assert Models.Detector(name="My Detector") in model.components


def test_remove_component():
    model = Models.InstrumentModel()
    model.add_detector("My Detector")
    model.remove_component(1)
    assert model.rowCount() == 1
    assert Models.Detector(name="My Detector") not in model.components
