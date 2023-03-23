import struct

from mock import Mock
from PySide6.Qt3DRender import Qt3DRender

from nexus_constructor.instrument_view.instrument_view_axes import InstrumentViewAxes


def test_GIVEN_int_list_WHEN_calling_create_data_array_THEN_original_list_can_be_recovered_by_unpacking_byte_array():
    list_size = 6
    original_list = [i for i in range(list_size)]

    byte_array = InstrumentViewAxes.create_data_array(original_list)
    unpacked_byte_array = struct.unpack("%sf" % len(original_list), byte_array)

    for i in range(list_size):
        assert original_list[i] == int(unpacked_byte_array[i])


def test_GIVEN_mesh_and_geometry_WHEN_calling_set_mesh_properties_THEN_mesh_properties_set():
    mesh = Mock()
    geometry = Mock()

    InstrumentViewAxes.set_mesh_properties(mesh, geometry)

    mesh.setPrimitiveType.assert_called_once_with(Qt3DRender.QGeometryRenderer.Lines)
    mesh.setGeometry.assert_called_once_with(geometry)
