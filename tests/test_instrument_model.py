from geometry_constructor import data_model
from geometry_constructor.instrument_model import InstrumentModel


def test_initialise_model():
    model = InstrumentModel()
    assert model.rowCount() == 1
    assert isinstance(model.components[0], data_model.Sample)


def test_add_component():
    model = InstrumentModel()
    model.add_detector('My Detector')
    assert model.rowCount() == 2
    assert isinstance(model.components[1], data_model.Detector)
    assert model.components[1].name == 'My Detector'


def test_remove_component():
    model = InstrumentModel()
    model.add_detector('My Detector')
    model.remove_component(1)
    assert model.rowCount() == 1
    assert not isinstance(model.components[0], data_model.Detector)


def test_replace_contents():
    model = InstrumentModel()
    replacement_data = [data_model.Sample(name='Replacement sample'),
                        data_model.Detector(name='Replacement Detector',
                                            geometry=data_model.OFFGeometry())]
    model.replace_contents(replacement_data)
    assert model.rowCount() == 2
    assert model.components == replacement_data
    assert len(model.meshes) == 2


def test_generate_component_name():
    model = InstrumentModel()
    model.components = [
        data_model.Component(name='Sample'),
        data_model.Component(name='Detector'),
        data_model.Component(name='Detector3'),
        data_model.Component(name='Magnet2'),
    ]
    assert model.generate_component_name('Sample') == 'Sample1'
    assert model.generate_component_name('Detector') == 'Detector4'
    assert model.generate_component_name('Magnet') == 'Magnet'
    assert model.generate_component_name('BeamGuide') == 'BeamGuide'
