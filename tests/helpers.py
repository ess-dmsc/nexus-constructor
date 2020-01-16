import uuid

import pytest

from nexus_constructor.instrument import Instrument
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.component.component import Component
import h5py
from typing import Any


def create_in_memory_file(filename):
    return h5py.File(filename, mode="x", driver="core", backing_store=False)


def add_component_to_file(
    nexus_wrapper: NexusWrapper,
    field_name: str = "test_field",
    field_value: Any = 42,
    component_name: str = "test_component",
) -> Component:
    component_group = nexus_wrapper.nexus_file.create_group(component_name)
    component_group.create_dataset(field_name, data=field_value)
    component = Component(nexus_wrapper, component_group)
    return component


class InMemoryFile(object):
    def __init__(self, filename):
        self.file_obj = h5py.File(
            filename, mode="x", driver="core", backing_store=False
        )

    def __enter__(self):
        return self.file_obj

    def __exit__(self, type, value, traceback):
        self.file_obj.close()


@pytest.fixture
def file():
    with InMemoryFile("test_file") as file:
        yield file


class TempInstrument(object):
    def __init__(self):
        self.wrapper = NexusWrapper(filename=str(uuid.uuid4()))
        self.instrument = Instrument(nexus_file=self.wrapper, definitions_dir="")

    def __enter__(self):
        return self.instrument

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wrapper.nexus_file.close()


@pytest.fixture
def instrument():
    with TempInstrument() as wrapper:
        yield wrapper
