from nexus_constructor.component.chopper_shape import ChopperShape
from nexus_constructor.component.component_shape import ComponentShape
from nexus_constructor.component.pixel_shape import PixelShape
from nexus_constructor.component.component_factory import create_component
from nexus_constructor.nexus import nexus_wrapper as nx

"""
Tests here document the conditions under which the factory creates components of different types
"""


def test_GIVEN_an_NXdisk_chopper_group_WHEN_calling_create_component_THEN_component_has_a_ChopperShape():
    wrapper = nx.NexusWrapper("file_with_chopper")
    chopper_group = wrapper.create_nx_group(
        "chopper", "NXdisk_chopper", wrapper.instrument
    )
    new_component = create_component(wrapper, chopper_group)
    assert isinstance(new_component._shape, ChopperShape)


def test_GIVEN_an_nx_group_with_no_shape_WHEN_calling_create_component_THEN_component_has_a_ComponentShape():
    wrapper = nx.NexusWrapper("file_with_component_with_no_shape")
    monitor_group = wrapper.create_nx_group("monitor", "NXmonitor", wrapper.instrument)
    new_component = create_component(wrapper, monitor_group)
    assert isinstance(new_component._shape, ComponentShape)


def test_GIVEN_an_NXdetector_group_with_detector_shape_WHEN_calling_create_component_THEN_component_has_a_ComponentShape():
    wrapper = nx.NexusWrapper("file_with_detector")
    detector_group = wrapper.create_nx_group(
        "detector", "NXdetector", wrapper.instrument
    )
    wrapper.create_nx_group("detector_shape", "NXoff_geometry", detector_group)
    new_component = create_component(wrapper, detector_group)
    assert isinstance(new_component._shape, ComponentShape)


def test_GIVEN_an_NXdetector_group_with_pixel_shape_WHEN_calling_create_component_THEN_component_has_a_PixelShape():
    wrapper = nx.NexusWrapper("file_with_detector")
    detector_group = wrapper.create_nx_group(
        "detector", "NXdetector", wrapper.instrument
    )
    wrapper.create_nx_group("pixel_shape", "NXoff_geometry", detector_group)
    new_component = create_component(wrapper, detector_group)
    assert isinstance(new_component._shape, PixelShape)
