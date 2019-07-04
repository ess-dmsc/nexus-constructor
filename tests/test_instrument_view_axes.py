import struct

from nexus_constructor.instrument_view_axes import InstrumentViewAxes


def test_GIVEN_int_list_WHEN_calling_create_data_array_THEN_original_can_be_recovered_by_converting_from_byte_to_int():

    list_size = 6
    original_list = [i for i in range(list_size)]

    byte_array = InstrumentViewAxes.create_data_array(original_list)
    unpacked_byte_array = struct.unpack("%sf" % len(original_list), byte_array)

    for i in range(list_size):
        assert original_list[i] == int(unpacked_byte_array[i])
