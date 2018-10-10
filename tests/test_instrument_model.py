from geometry_constructor import Models


def test_initialise_model():
    model = Models.InstrumentModel()
    assert model.rowCount() == 1
    assert isinstance(model.components[0], Models.Sample)


def test_add_component():
    model = Models.InstrumentModel()
    model.add_detector('My Detector')
    assert model.rowCount() == 2
    assert isinstance(model.components[1], Models.Detector)
    assert model.components[1].name == 'My Detector'


def test_remove_component():
    model = Models.InstrumentModel()
    model.add_detector('My Detector')
    model.remove_component(1)
    assert model.rowCount() == 1
    assert not isinstance(model.components[0], Models.Detector)
