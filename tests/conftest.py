"""Set up the shared library and one native sample run for project tests."""

import json

import pytest

from support import ROOT, native


@pytest.fixture(scope="session", autouse=True)
def prepared_library():
    result = native("project", "sync", "--project", str(ROOT))
    assert result.returncode == 0, result.stderr


@pytest.fixture(scope="session")
def sample_run(tmp_path_factory, prepared_library):
    output = tmp_path_factory.mktemp("sample-output")
    result = native("run", "--sample", "--project", str(ROOT), "--output", str(output))
    records = list(output.glob("*/run.json"))
    assert len(records) == 1, result.stdout + result.stderr
    record_path = records[0]
    return (
        result.returncode,
        record_path.parent,
        json.loads(record_path.read_text(encoding="utf-8")),
    )
