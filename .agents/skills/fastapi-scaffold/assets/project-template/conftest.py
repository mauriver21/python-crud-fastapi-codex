import os

os.environ["APP_ENV"] = "test"

import pytest

from tests.utils import initialize_test_user


@pytest.fixture(scope="session", autouse=True)
def setup_tests():
    initialize_test_user()
