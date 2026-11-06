"""check.py summarizes sample findings by code instead of linking a deleted report."""

from check import finding_summary


def entry(*checks):
    return {"checks": [{"code": code, "status": status} for code, status in checks]}


def test_findings_are_grouped_by_code_with_failures_first():
    record = {
        "entries": [
            entry(("content.multiple_links", "warn"), ("layout.fits", "pass")),
            entry(("content.multiple_links", "warn"), ("output.identity", "fail")),
            entry(
                ("source.address_incomplete", "warn"), ("qr.absent", "not_applicable")
            ),
        ],
        "checks": [],
    }
    assert finding_summary(record) == [
        "fail  output.identity: 1 notice",
        "warn  content.multiple_links: 2 notices",
        "warn  source.address_incomplete: 1 notice",
    ]


def test_repeated_code_on_one_notice_counts_once():
    record = {
        "entries": [entry(("data.history", "warn"), ("data.history", "warn"))],
        "checks": [],
    }
    assert finding_summary(record) == ["warn  data.history: 1 notice"]


def test_run_level_failure_shows_its_message():
    record = {
        "entries": [],
        "checks": [
            {"code": "run.failed", "status": "fail", "message": "Typst not found"}
        ],
    }
    assert finding_summary(record) == ["fail  run.failed: Typst not found"]


def test_clean_run_has_no_summary():
    assert (
        finding_summary({"entries": [entry(("layout.fits", "pass"))], "checks": []})
        == []
    )


def test_prepare_calls_native_cli_and_reads_versioned_json(monkeypatch):
    import json
    import subprocess
    import check

    calls = []

    def fake(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(
            command, 0, json.dumps({"schema_version": 1, "entries": [{}]}), ""
        )

    monkeypatch.setattr(check, "immuknow_command", lambda: "immuknow")
    monkeypatch.setattr(check.subprocess, "run", fake)
    assert len(check.prepare_sample()["entries"]) == 1
    assert calls[0][0:2] == ["immuknow", "prepare"]
    assert "--notice-assignments" in calls[0]


def test_prepare_surfaces_cli_errors(monkeypatch):
    import subprocess
    import pytest
    import check

    monkeypatch.setattr(check, "immuknow_command", lambda: "immuknow")
    monkeypatch.setattr(
        check.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 1, "", "Invalid assignment"
        ),
    )
    with pytest.raises(ValueError, match="Invalid assignment"):
        check.prepare_sample()


def test_effective_findings_override_observed_statuses():
    record = {
        "entries": [
            {
                "checks": [
                    {"code": "adjusted", "status": "warn"},
                    {"code": "disabled", "status": "warn"},
                ],
                "effective_checks": [
                    {"code": "adjusted", "status": "fail"},
                    {"code": "disabled", "status": "not_run"},
                ],
            },
            entry(("fallback", "warn")),
        ],
        "checks": [],
    }
    assert finding_summary(record) == [
        "fail  adjusted: 1 notice",
        "warn  fallback: 1 notice",
    ]


def test_artifact_and_run_errors_explain_failed_output():
    record = {
        "entries": [
            {
                "row_key": "row-000001",
                "checks": [],
                "original": {"status": "failed", "error": "Template failed"},
                "encryption": {"status": "failed", "error": "Password field missing"},
            }
        ],
        "checks": [],
        "error": "Bundle assembly failed",
    }
    assert finding_summary(record) == [
        "fail  row-000001 original PDF: Template failed",
        "fail  row-000001 encrypted copy: Password field missing",
        "fail  run: Bundle assembly failed",
    ]
