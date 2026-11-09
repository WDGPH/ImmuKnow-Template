"""The fictional sample completes one native run and retains every notice."""

import csv
from pathlib import Path

import pytest

from project import SAMPLE_INPUT

pytestmark = pytest.mark.pipeline


def test_sample_exits_without_failures(sample_run):
    code, _, record = sample_run
    assert code == 0, record["status"]
    assert record["status"] in {"completed", "completed_with_warnings"}


def test_every_sample_notice_is_produced(sample_run):
    _, directory, record = sample_run
    with SAMPLE_INPUT.open(encoding="utf-8-sig", newline="") as source:
        expected = list(csv.DictReader(source))
    entries = record["entries"]
    assert len(expected) == len(entries)
    assert entries, "The fictional sample must contain at least one client"
    for row, entry in zip(expected, entries, strict=True):
        assert entry["source"] == row
        assert entry["original"]["status"] == "completed"
        assert (directory / entry["original"]["path"]).is_file()
        assert all(check["status"] != "fail" for check in entry["checks"])


def test_starter_filename_settings_reach_native_artifacts(sample_run):
    _, directory, record = sample_run
    assert record["configured_settings"]["filenames"]["individual"]["template"] == (
        "{client_id}_{notice_variant}_{language_code}"
    )
    for entry in record["entries"]:
        name = Path(entry["original"]["path"]).name
        assert name == (
            f"{entry['client_id']}_{entry['assignment']['version_id']}_"
            f"{entry['assignment']['language']}.pdf"
        )
        assert not any(c["code"] == "output.filename_fallback" for c in entry["checks"])
    for bundle in record["bundles"]:
        assert Path(bundle["path"]).name.startswith(bundle["route"] + "_")
        assert Path(bundle["path"]).stem == Path(bundle["csv"]).stem
        assert (directory / bundle["path"]).is_file()
        assert (directory / bundle["csv"]).is_file()
