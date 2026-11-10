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
    assert (
        record_headers
        == "run_id,record_revision,bundle_attempt,row_key,source_record,client_id,name,school,notice_variant,language,severity,evaluation_state,route,hold_reason,original_status,original_path,original_pages,protected_status,protected_path,bundle_status,bundle_path,bundle_start_page,bundle_end_page".split(
            ","
        )
    )
    assert (
        finding_headers
        == "run_id,record_revision,bundle_attempt,scope,attempt_number,row_key,client_id,finding_key,origin,code,observed_status,effective_status,disabled,policy_reason,component,page,message,issue_ids,acknowledged_issue_ids".split(
            ","
        )
    )
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


def test_hold_release_keeps_prior_bundle_and_export_snapshots(sample_run, tmp_path):
    import hashlib
    import json
    import shutil
    import subprocess
    from project import immuknow_command

    _, directory, original = sample_run
    copied = tmp_path / "run"
    shutil.copytree(directory, copied)
    key = original["entries"][0]["row_key"]
    old_files = [
        copied / original["exports"][name]["path"] for name in ("records", "findings")
    ]
    old_files += [copied / bundle["path"] for bundle in original["bundles"]]
    hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in old_files}
    held = subprocess.run(
        [
            immuknow_command(),
            "rebundle",
            str(copied),
            "--withhold",
            key,
            "--reason",
            "Fictional review",
        ],
        capture_output=True,
        text=True,
    )
    assert held.returncode == 0, held.stderr
    hold_record = json.loads((copied / "run.json").read_text())
    _, rows = selected_csv(copied, hold_record, "records")
    row = next(row for row in rows if row["row_key"] == key)
    assert (row["route"], row["bundle_status"], row["bundle_path"]) == (
        "withheld",
        "excluded",
        "",
    )
    assert row["bundle_start_page"] == row["bundle_end_page"] == ""
    hold_exports = [
        copied / hold_record["exports"][name]["path"]
        for name in ("records", "findings")
    ]
    hold_exports += [copied / bundle["path"] for bundle in hold_record["bundles"]]
    hashes.update(
        {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in hold_exports}
    )
    released = subprocess.run(
        [immuknow_command(), "rebundle", str(copied), "--release", key],
        capture_output=True,
        text=True,
    )
    assert released.returncode == 0, released.stderr
    release_record = json.loads((copied / "run.json").read_text())
    _, rows = selected_csv(copied, release_record, "records")
    row = next(row for row in rows if row["row_key"] == key)
    assert row["route"] == "ready" and row["bundle_status"] == "completed"
    assert (
        release_record["active_bundle_attempt"] == original["active_bundle_attempt"] + 2
    )
    assert all(
        hashlib.sha256(path.read_bytes()).hexdigest() == digest
        for path, digest in hashes.items()
    )


def test_failed_preparation_and_requested_protected_copy(tmp_path):
    import json
    import shutil

    from pypdf import PdfReader
    import run
    from project import CONFIG_DIR, TEMPLATES_DIR

    with SAMPLE_INPUT.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames
        sample = [next(reader), next(reader)]
    sample[0]["immunizations_given"] = "not a valid history"
    source = tmp_path / "fictional.csv"
    with source.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sample)
    config = tmp_path / "config"
    shutil.copytree(CONFIG_DIR, config)
    parameters = config / "parameters.yaml"
    text = parameters.read_text().replace(
        "encryption:\n  enabled: false", "encryption:\n  enabled: true"
    )
    parameters.write_text(text)
    output = tmp_path / "runs"
    code = run.main(
        [
            str(source),
            "--template",
            str(TEMPLATES_DIR / "overdue_agents.en.typ"),
            "--config",
            str(config),
            "--output",
            str(output),
        ]
    )
    assert code != 0
    (record_path,) = output.glob("*/run.json")
    record = json.loads(record_path.read_text())
    _, rows = selected_csv(record_path.parent, record, "records")
    assert (rows[0]["severity"], rows[0]["route"], rows[0]["protected_status"]) == (
        "error",
        "report_only",
        "excluded",
    )
    assert rows[0]["original_path"] == "" and rows[0]["protected_path"] == ""
    assert (
        rows[1]["original_status"] == "completed"
        and rows[1]["protected_status"] == "completed"
    )
    import hashlib

    protected = (record_path.parent / rows[1]["protected_path"]).read_bytes()
    assert protected.startswith(b"%PDF-") and b"/Encrypt" in protected
    assert (
        hashlib.sha256(protected).hexdigest()
        == record["entries"][1]["encryption"]["sha256"]
    )
    assert record["entries"][1]["encryption"]["revision"] == 6
    assert len(PdfReader(record_path.parent / rows[1]["original_path"]).pages) == int(
        rows[1]["original_pages"]
    )
