from nexus_constructor.nexus_model import (
    NexusModel,
    get_nx_class_for_component,
    create_group,
    delete_group,
    ComponentType,
    append_nxs_extension,
)
from pytest import raises
import h5py

sample_name = "NXsample"
detector_name = "NXdetector"
monitor_name = "NXmonitor"
source_name = "NXsource"
slit_name = "NXslit"
moderator_name = "NXmoderator"
chopper_name = "NXdisk_chopper"
instrument_name = "NXinstrument"
entry_name = "NXentry"


def test_GIVEN_detector_WHEN_get_nx_class_THEN_returns_correct_component_name():
    component = ComponentType.DETECTOR
    assert get_nx_class_for_component(component) == detector_name


def test_GIVEN_sample_WHEN_get_nx_class_THEN_returns_correct_component_name():
    component = ComponentType.SAMPLE
    assert get_nx_class_for_component(component) == sample_name


def test_GIVEN_monitor_WHEN_get_nx_class_THEN_returns_correct_component_name():
    component = ComponentType.MONITOR
    assert get_nx_class_for_component(component) == monitor_name


def test_GIVEN_source_WHEN_get_nx_class_THEN_returns_correct_component_name():
    component = ComponentType.SOURCE
    assert get_nx_class_for_component(component) == source_name


def test_GIVEN_slit_WHEN_get_nx_class_THEN_returns_correct_component_name():
    component = ComponentType.SLIT
    assert get_nx_class_for_component(component) == slit_name


def test_GIVEN_moderator_WHEN_get_nx_class_THEN_returns_correct_component_name():
    component = ComponentType.MODERATOR
    assert get_nx_class_for_component(component) == moderator_name


def test_GIVEN_chopper_WHEN_get_nx_class_THEN_returns_correct_component_name():
    component = ComponentType.DISK_CHOPPER
    assert get_nx_class_for_component(component) == chopper_name


def test_GIVEN_nothing_WHEN_creating_nexus_model_THEN_creates_entry_group_with_correct_nx_class():
    model = NexusModel()
    assert model.getEntryGroup().attrs["NX_class"] == entry_name


def test_GIVEN_nonstandard_nxclass_WHEN_creating_group_THEN_group_is_still_created():
    name = "test"
    nx_class = "NXarbitrary"
    nexus_file = h5py.File(name, driver="core", backing_store=False)
    create_group(name, nx_class, nexus_file)

    assert nexus_file[name].attrs["NX_class"] == nx_class


def test_GIVEN_recognised_name_WHEN_deleting_group_THEN_group_gets_deleted():
    file_name = "test2"
    nx_class = "NXarbitrary"
    component_name = "MyDetector"
    nexus_file = h5py.File(file_name, driver="core", backing_store=False)
    create_group(component_name, nx_class, nexus_file)
    delete_group(component_name, nexus_file)

    with raises(KeyError):
        nexus_file[component_name]


def test_GIVEN_unrecognised_name_WHEN_deleting_group_THEN_throws():
    file_name = "test3"
    nx_class = "NXarbitrary"
    component_name = "MyDetector"
    nexus_file = h5py.File(file_name, driver="core", backing_store=False)
    create_group(component_name, nx_class, nexus_file)

    with raises(KeyError):
        delete_group("wrongname", nexus_file)


def test_GIVEN_repeated_name_WHEN_creating_component_that_shares_its_name_with_deleted_component_THEN_creation_successful():
    file_name = "test4"
    nx_class = "NXarbitrary"
    component_name = "MyDetector"
    nexus_file = h5py.File(file_name, driver="core", backing_store=False)
    create_group(component_name, nx_class, nexus_file)
    delete_group(component_name, nexus_file)
    create_group(component_name, nx_class, nexus_file)


def test_GIVEN_string_ending_with_nxs_WHEN_appending_nxs_extension_THEN_string_is_not_changed():
    file_name = "test.nxs"
    assert file_name == append_nxs_extension(file_name)


def test_GIVEN_string_not_ending_in_nxs_WHEN_appending_nxs_extension_THEN_extension_is_appended():
    file_name = "test"
    assert file_name + ".nxs" == append_nxs_extension(file_name)
