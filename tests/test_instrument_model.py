from geometry_constructor import data_model
from geometry_constructor.instrument_model import InstrumentModel


def test_initialise_model():
    model = InstrumentModel()
    assert model.rowCount() == 1
    assert model.components[0].component_type == data_model.ComponentType.SAMPLE


def test_add_component():
    model = InstrumentModel()
    model.add_component('Detector', 'My Detector')
    assert model.rowCount() == 2
    assert model.components[1].component_type == data_model.ComponentType.DETECTOR
    assert model.components[1].name == 'My Detector'


def test_remove_component():
    model = InstrumentModel()
    model.add_component('Detector', 'My Detector')
    model.remove_component(1)
    assert model.rowCount() == 1
    assert not model.components[0].component_type == data_model.ComponentType.DETECTOR
    # The sample at index 0 shouldn't be removable
    model.remove_component(0)
    assert model.rowCount() == 1
    assert model.components[0].component_type == data_model.ComponentType.SAMPLE


def test_replace_contents():
    model = InstrumentModel()
    replacement_data = [data_model.Component(component_type=data_model.ComponentType.SAMPLE,
                                             name='Replacement sample'),
                        data_model.Component(component_type=data_model.ComponentType.DETECTOR,
                                             name='Replacement Detector',
                                             geometry=data_model.OFFGeometry())]
    model.replace_contents(replacement_data)
    assert model.rowCount() == 2
    assert model.components == replacement_data


def test_generate_component_name():
    model = InstrumentModel()
    model.components = [
        data_model.Component(component_type=data_model.ComponentType.SAMPLE, name='Sample'),
        data_model.Component(component_type=data_model.ComponentType.SAMPLE, name='Detector'),
        data_model.Component(component_type=data_model.ComponentType.SAMPLE, name='Detector3'),
        data_model.Component(component_type=data_model.ComponentType.SAMPLE, name='Magnet2'),
    ]
    assert model.generate_component_name('Sample') == 'Sample1'
    assert model.generate_component_name('Detector') == 'Detector4'
    assert model.generate_component_name('Magnet') == 'Magnet'
    assert model.generate_component_name('BeamGuide') == 'BeamGuide'


def test_is_removable():
    model = InstrumentModel()
    model.components = [data_model.Component(component_type=data_model.ComponentType.SAMPLE,
                                             name=str(i)) for i in range(4)]
    model.components[0].transform_parent = model.components[0]
    model.components[1].transform_parent = model.components[0]
    model.components[2].transform_parent = model.components[1]
    model.components[3].transform_parent = model.components[3]

    assert not model.is_removable(0)
    assert not model.is_removable(1)
    assert model.is_removable(2)
    assert model.is_removable(3)
