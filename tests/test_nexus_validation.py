from nexus_constructor.nexus.validation import validate_group, ValidateDataset
import numpy as np
import pytest

pytest.skip("Disabled whilst working on model change", allow_module_level=True)


def test_validate_dataset_reports_problem_when_expected_dataset_is_not_present(
    nexus_wrapper,
):
    nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, "a_dataset", 0)

    dataset_name = "test_dataset"
    validator = ValidateDataset(dataset_name)
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) > 0
    ), "Expected there to be a reported problem because dataset is not present"


def test_validate_dataset_does_not_report_problem_when_expected_dataset_is_present(
    nexus_wrapper,
):
    dataset_name = "test_dataset"
    nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, dataset_name, 0)

    validator = ValidateDataset(dataset_name)
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) == 0
    ), "Expected there to be no reported problem because dataset is present"


def test_validate_dataset_reports_problem_when_expected_attribute_is_not_present(
    nexus_wrapper,
):
    dataset_name = "test_dataset"
    nexus_wrapper.set_field_value(nexus_wrapper.nexus_file, dataset_name, 0)

    validator = ValidateDataset(dataset_name, attributes={"test_attribute": None})
    problems = []
    validator.check(nexus_wrapper.nexus_file, problems)
    assert (
        len(problems) > 0
    ), "Expected there to be a reported problem because attribute is not present"


def test_validate_dataset_does_not_report_problem_when_expected_attribute_is_present(
    nexus_wrapper,
):
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


def test_validate_dataset_reports_problem_when_attribute_does_not_have_expected_value(
    nexus_wrapper,
):
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


def test_validate_dataset_does_not_report_problem_when_attribute_has_expected_value(
    nexus_wrapper,
):
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


def test_validate_dataset_reports_problem_when_dataset_does_not_have_expected_shape(
    nexus_wrapper,
):
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


def test_validate_dataset_does_not_report_problem_when_dataset_has_expected_shape(
    nexus_wrapper,
):
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


def test_validate_group_reports_problem_when_group_does_not_have_an_nx_class(
    nexus_wrapper,
):
    group = nexus_wrapper.create_nx_group(
        "test_group", "NXsomething", nexus_wrapper.nexus_file
    )
    nexus_wrapper.delete_attribute(group, "NX_class")

    problems = validate_group(group, "NXsomething", ())
    assert (
        len(problems) > 0
    ), "Expected there to be a reported problem because group does not have an nx_class attribute"


def test_validate_group_reports_problem_when_group_does_not_have_expected_nx_class(
    nexus_wrapper,
):
    group = nexus_wrapper.create_nx_group(
        "test_group", "NXsomething", nexus_wrapper.nexus_file
    )

    problems = validate_group(group, "NXtest", ())
    assert (
        len(problems) > 0
    ), "Expected there to be a reported problem because group does not have expected NX_class"


def test_validate_group_does_not_report_problem_when_group_has_expected_nx_class(
    nexus_wrapper,
):
    nexus_class = "NXtest"
    group = nexus_wrapper.create_nx_group(
        "test_group", nexus_class, nexus_wrapper.nexus_file
    )

    problems = validate_group(group, nexus_class, ())
    assert (
        len(problems) == 0
    ), "Expected there to be no reported problem because group has expected NX_class"
