from geometry_constructor import DataModel
from geometry_constructor.QmlModel import InstrumentModel


def test_initialise_model():
    model = InstrumentModel()
    assert model.rowCount() == 1
    assert isinstance(model.components[0], DataModel.Sample)


def test_add_component():
    model = InstrumentModel()
    model.add_detector('My Detector')
    assert model.rowCount() == 2
    assert isinstance(model.components[1], DataModel.Detector)
    assert model.components[1].name == 'My Detector'


def test_remove_component():
    model = InstrumentModel()
    model.add_detector('My Detector')
    model.remove_component(1)
    assert model.rowCount() == 1
    assert not isinstance(model.components[0], DataModel.Detector)
