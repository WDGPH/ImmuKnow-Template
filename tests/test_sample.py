"""The sample runs end to end through the installed ImmuKnow and Typst."""

import csv
import json

import pytest

import run
from project import SAMPLE_ASSIGNMENTS, SAMPLE_INPUT

pytestmark = pytest.mark.pipeline


@pytest.fixture(scope="module")
def sample_run(tmp_path_factory):
    output = tmp_path_factory.mktemp("output")
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
    return code, json.loads(record_path.read_text(encoding="utf-8"))


def test_sample_exits_zero(sample_run):
    code, record = sample_run
    assert code == 0, record["status"]


def test_every_sample_notice_is_produced(sample_run):
    _, record = sample_run
    assert record["status"] in {"completed", "completed_with_warnings"}
    with SAMPLE_INPUT.open(encoding="utf-8-sig", newline="") as source:
        expected = len(list(csv.DictReader(source)))
    assert expected > 0
    assert [e["original"]["status"] for e in record["entries"]] == [
        "completed"
    ] * expected


def test_no_sample_check_fails(sample_run):
    _, record = sample_run
    failures = [
        (entry["client_id"], check["code"])
        for entry in record["entries"]
        for check in entry["checks"]
        if check["status"] == "fail"
    ]
    assert failures == []
