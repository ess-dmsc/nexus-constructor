from nexus_constructor.nexus.validation import ValidateDataset
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
import numpy as np


def test_validate_dataset_reports_problem_when_expected_dataset_is_not_present():
    nexus_wrapper = NexusWrapper()
    nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, "a_dataset", 0)

    dataset_name = "test_dataset"
    validator = ValidateDataset(dataset_name)
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) > 0
    ), "Expected there to be a reported problem because dataset is not present"


def test_validate_dataset_does_not_report_problem_when_expected_dataset_is_present():
    nexus_wrapper = NexusWrapper()
    dataset_name = "test_dataset"
    nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, dataset_name, 0)

    validator = ValidateDataset(dataset_name)
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) == 0
    ), "Expected there to be no reported problem because dataset is present"


def test_validate_dataset_reports_problem_when_expected_attribute_is_not_present():
    nexus_wrapper = NexusWrapper()
    dataset_name = "test_dataset"
    nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, dataset_name, 0)

    validator = ValidateDataset(dataset_name, attributes={"test_attribute": None})
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) > 0
    ), "Expected there to be a reported problem because attribute is not present"


def test_validate_dataset_does_not_report_problem_when_expected_attribute_is_present():
    nexus_wrapper = NexusWrapper()
    dataset_name = "test_dataset"
    dataset = nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, dataset_name, 0)
    attr_name = "test_attribute"
    nexus_wrapper.set_attribute_value(dataset, attr_name, 0)

    validator = ValidateDataset(dataset_name, attributes={attr_name: None})
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) == 0
    ), "Expected there to be no reported problem because attribute is present"


def test_validate_dataset_reports_problem_when_attribute_does_not_have_expected_value():
    nexus_wrapper = NexusWrapper()
    dataset_name = "test_dataset"
    dataset = nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, dataset_name, 0)
    attr_name = "test_attribute"
    attr_value = 42
    nexus_wrapper.set_attribute_value(dataset, attr_name, attr_value)

    expected_value = 0
    validator = ValidateDataset(dataset_name, attributes={attr_name: expected_value})
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) > 0
    ), "Expected there to be a reported problem because attribute does not have expected value"


def test_validate_dataset_does_not_report_problem_when_attribute_has_expected_value():
    nexus_wrapper = NexusWrapper()
    dataset_name = "test_dataset"
    dataset = nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, dataset_name, 0)
    attr_name = "test_attribute"
    attr_value = 42
    nexus_wrapper.set_attribute_value(dataset, attr_name, attr_value)

    validator = ValidateDataset(dataset_name, attributes={attr_name: attr_value})
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) == 0
    ), "Expected there to be no reported problem because attribute has expected value"


def test_validate_dataset_reports_problem_when_dataset_does_not_have_expected_shape():
    nexus_wrapper = NexusWrapper()
    dataset_name = "test_dataset"
    dataset_value = np.array(list(range(12)))
    dataset_shape = (3, 4)
    dataset_value = np.reshape(dataset_value, dataset_shape)
    nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, dataset_name, dataset_value)

    validator = ValidateDataset(dataset_name, shape=(1, 2))
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) > 0
    ), "Expected there to be a reported problem because dataset does not have expected shape"


def test_validate_dataset_does_not_report_problem_when_dataset_has_expected_shape():
    nexus_wrapper = NexusWrapper()
    dataset_name = "test_dataset"
    dataset_value = np.array(list(range(12)))
    dataset_shape = (3, 4)
    dataset_value = np.reshape(dataset_value, dataset_shape)
    nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, dataset_name, dataset_value)

    validator = ValidateDataset(dataset_name, shape=dataset_shape)
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) == 0
    ), "Expected there to be no reported problem because dataset has expected shape"
