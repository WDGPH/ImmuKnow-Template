"""Set up the shared library and one native sample run for project tests."""

import json

import pytest

import run
from project import SAMPLE_ASSIGNMENTS, SAMPLE_INPUT, TEMPLATES_DIR
from sync_lib import ensure_library


@pytest.fixture(scope="session", autouse=True)
def prepared_library():
    ensure_library(TEMPLATES_DIR)


@pytest.fixture(scope="session")
def sample_run(tmp_path_factory, prepared_library):
    output = tmp_path_factory.mktemp("sample-output")
    code = run.main(
        [
            str(SAMPLE_INPUT),
            "--notice-assignments",
            str(SAMPLE_ASSIGNMENTS),
            "--output",
            str(output),
        ]
    )
    (record_path,) = output.glob("*/run.json")
    return code, record_path.parent, json.loads(record_path.read_text(encoding="utf-8"))
