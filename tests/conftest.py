from tests.chopper_test_helpers import chopper_details  # noqa: F401

# Share the fixtures contained in ui_test_utils with all tests
pytest_plugins = ["tests.ui_tests.ui_test_utils"]
