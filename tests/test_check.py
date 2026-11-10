"""check.py summarizes sample findings by code instead of linking a deleted report."""

from check import finding_summary


def entry(*checks):
    observed = [
        {"finding_key": f"check-{i:06}", "code": code, "status": status}
        for i, (code, status) in enumerate(checks, 1)
    ]
    return {
        "checks": observed,
        "effective_checks": [
            {
                "finding_key": check["finding_key"],
                "status": check["status"],
                "disabled": False,
                "policy_reason": None,
            }
            for check in observed
        ],
    }


def test_findings_are_grouped_by_code_with_failures_first():
    record = {
        "run_schema_version": 2,
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
        "run_schema_version": 2,
        "entries": [entry(("data.history", "warn"), ("data.history", "warn"))],
        "checks": [],
    }
    assert finding_summary(record) == ["warn  data.history: 1 notice"]


def test_run_level_failure_shows_its_message():
    record = {
        "run_schema_version": 2,
        "entries": [],
        "checks": [
            {"code": "run.failed", "status": "fail", "message": "Typst not found"}
        ],
    }
    assert finding_summary(record) == ["fail  run.failed: Typst not found"]


def test_clean_run_has_no_summary():
    assert (
        finding_summary(
            {
                "run_schema_version": 2,
                "entries": [entry(("layout.fits", "pass"))],
                "checks": [],
            }
        )
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
            command, 0, json.dumps({"schema_version": 2, "entries": [{}]}), ""
        )

    monkeypatch.setattr(check, "immuknow_command", lambda: "immuknow")
    monkeypatch.setattr(check.subprocess, "run", fake)
    assert len(check.prepare_sample()["entries"]) == 1
    assert calls[0][0:2] == ["immuknow", "prepare"]
    assert "--notice-assignments" in calls[0]


def test_prepare_surfaces_failed_row_findings(monkeypatch):
    import json
    import subprocess
    import pytest
    import check

    result = {
        "schema_version": 2,
        "entries": [
            {
                "row_key": "row-000001",
                "checks": [{"code": "source.history_unusable", "status": "fail"}],
            }
        ],
    }
    monkeypatch.setattr(check, "immuknow_command", lambda: "immuknow")
    monkeypatch.setattr(
        check.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 0, json.dumps(result), ""
        ),
    )
    with pytest.raises(ValueError, match="Sample preparation contains failed rows"):
        check.prepare_sample()


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
    adjusted = entry(("adjusted", "warn"), ("disabled", "warn"))
    adjusted["effective_checks"][0]["status"] = "fail"
    adjusted["effective_checks"][1].update(
        status="not_run", disabled=True, policy_reason="Reviewed"
    )
    record = {
        "run_schema_version": 2,
        "status": "completed",
        "entries": [adjusted, entry(("fallback", "warn"))],
        "checks": [],
    }
    assert finding_summary(record) == [
        "fail  adjusted: 1 notice",
        "warn  fallback: 1 notice",
    ]


def test_partial_run_uses_observations_and_completed_run_requires_joins():
    import pytest

    partial = {
        "run_schema_version": 2,
        "status": "failed",
        "entries": [{"checks": [{"code": "source.issue", "status": "warn"}]}],
        "checks": [],
    }
    assert finding_summary(partial) == ["warn  source.issue: 1 notice"]
    partial["status"] = "completed"
    with pytest.raises(ValueError, match="missing effective"):
        finding_summary(partial)
    bad = {
        "run_schema_version": 2,
        "status": "completed",
        "entries": [entry(("one", "warn"), ("two", "warn"))],
        "checks": [],
    }
    bad["entries"][0]["effective_checks"][1]["finding_key"] = bad["entries"][0][
        "effective_checks"
    ][0]["finding_key"]
    with pytest.raises(ValueError, match="do not match"):
        finding_summary(bad)


def test_artifact_and_run_errors_explain_failed_output():
    record = {
        "run_schema_version": 2,
        "entries": [
            {
                "row_key": "row-000001",
                "checks": [],
                "effective_checks": [],
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


def test_saved_run_version_is_required():
    import pytest

    with pytest.raises(ValueError, match="Unsupported saved-run version"):
        finding_summary({"run_schema_version": 1, "entries": [], "checks": []})
