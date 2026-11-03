"""Materialize the locked shared library for authored starter presentation tests."""

import pytest

from project import TEMPLATES_DIR
from sync_lib import ensure_library


@pytest.fixture(scope="session", autouse=True)
def prepared_library():
    ensure_library(TEMPLATES_DIR)
