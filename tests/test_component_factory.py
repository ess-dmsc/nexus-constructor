from nexus_constructor.chopper_component import ChopperComponent
from nexus_constructor.component import Component
from nexus_constructor.component_factory import create_component
from nexus_constructor.nexus import nexus_wrapper as nx


def test_GIVEN_an_NXdisk_chopper_group_WHEN_calling_create_component_THEN_a_ChopperComponent_is_created():
    wrapper = nx.NexusWrapper("file_with_chopper")
    chopper_group = wrapper.create_nx_group(
        "chopper", "NXdisk_chopper", wrapper.instrument
    )
    new_component = create_component(wrapper, chopper_group)
    assert isinstance(new_component, ChopperComponent)


def test_GIVEN_an_nx_group_with_no_shape_WHEN_calling_create_component_THEN_a_Component_is_created():
    wrapper = nx.NexusWrapper("file_with_component_with_no_shape")
    monitor_group = wrapper.create_nx_group("monitor", "NXmonitor", wrapper.instrument)
    new_component = create_component(wrapper, monitor_group)
    assert isinstance(new_component, Component)


def test_GIVEN_an_NXdetector_group_with_detector_shape_WHEN_calling_create_component_THEN_a_Component_is_created():
    wrapper = nx.NexusWrapper("file_with_detector")
    detector_group = wrapper.create_nx_group(
        "detector", "NXdetector", wrapper.instrument
    )
    wrapper.create_nx_group("detector_shape", "NXoff_geometry", detector_group)
    new_component = create_component(wrapper, detector_group)
    assert isinstance(new_component, Component)


def test_GIVEN_an_NXdetector_group_with_pixel_shape_WHEN_calling_create_component_THEN_a_PixelShapeComponent_is_created():
    wrapper = nx.NexusWrapper("file_with_detector")
    detector_group = wrapper.create_nx_group(
        "detector", "NXdetector", wrapper.instrument
    )
    wrapper.create_nx_group("pixel_shape", "NXoff_geometry", detector_group)
    new_component = create_component(wrapper, detector_group)
    assert isinstance(new_component, PixelShapeComponent)
