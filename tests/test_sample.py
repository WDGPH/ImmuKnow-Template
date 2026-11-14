"""The fictional sample completes one native run and retains every notice."""

import csv
from pathlib import Path

import pytest

from support import SAMPLE_INPUT

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
        assert (directory / bundle["path"]).is_file()
        assert "csv" not in bundle


def selected_csv(directory, record, name):
    import hashlib

    exports = record["exports"]
    assert exports["schema_version"] == 1
    assert exports["record_revision"] == record["record_revision"]
    descriptor = exports[name]
    path = directory / descriptor["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == descriptor["sha256"]
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        return reader.fieldnames, list(reader)


def test_sample_exports_join_source_records_and_pdf_ranges(sample_run):
    from pypdf import PdfReader

    _, directory, record = sample_run
    record_headers, rows = selected_csv(directory, record, "records")
    finding_headers, findings = selected_csv(directory, record, "findings")
    assert {
        "row_key",
        "source_record",
        "client_id",
        "original_status",
        "original_path",
        "protected_status",
        "bundle_status",
        "bundle_path",
        "bundle_start_page",
        "bundle_end_page",
    } <= set(record_headers)
    assert {"scope", "row_key", "client_id"} <= set(finding_headers)
    row_ids = {row["row_key"]: row["client_id"] for row in rows}
    row_findings = [finding for finding in findings if finding["scope"] == "row"]
    assert row_findings
    assert all(
        row_ids[finding["row_key"]] == finding["client_id"] for finding in row_findings
    )
    assert len(rows) == len(record["entries"])
    for index, (row, entry) in enumerate(zip(rows, record["entries"], strict=True), 1):
        assert row["row_key"] == entry["row_key"]
        assert row["source_record"] == str(index)
        assert row["client_id"] == entry["client_id"]
        assert row["original_status"] == "completed"
        assert row["original_path"] == entry["original"]["path"]
        assert row["protected_status"] == "not_requested"
        assert row["bundle_status"] == "completed"
        assert row["bundle_path"] == entry["bundle"]["path"]
        assert int(row["bundle_end_page"]) - int(row["bundle_start_page"]) + 1 == len(
            PdfReader(directory / row["original_path"]).pages
        )
        assert int(row["bundle_end_page"]) <= len(
            PdfReader(directory / row["bundle_path"]).pages
        )
    assert not (directory / "report.html").exists()
    assert not list(directory.glob("bundles-*/*.csv"))
