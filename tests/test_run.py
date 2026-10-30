"""run.py builds the immuknow command and passes its exit code through."""

import json
import subprocess

import pytest

import run
from project import CONFIG_DIR, OUTPUT_DIR, TEMPLATES_DIR


@pytest.fixture
def fake_immuknow(monkeypatch, tmp_path):
    """Record the command instead of running ImmuKnow; optionally write a run record."""
    calls = []
    result = {"returncode": 0, "status": None}

    def fake_run(command, *args, **kwargs):
        calls.append(command)
        if result["status"]:
            output = command[command.index("--output") + 1]
            run_dir = tmp_path / "out" / "20260101T000000000000"
            assert output == str(tmp_path / "out")
            run_dir.mkdir(parents=True)
            (run_dir / "run.json").write_text(json.dumps({"status": result["status"]}))
        return subprocess.CompletedProcess(command, result["returncode"])

    monkeypatch.setattr(run, "immuknow_command", lambda: "immuknow")
    monkeypatch.setattr(run.subprocess, "run", fake_run)
    return calls, result


def test_assignments_use_project_directories(fake_immuknow):
    calls, _ = fake_immuknow
    assert run.main(["cohort.csv", "--notice-assignments", "a.json"]) == 0
    assert calls == [
        [
            "immuknow", "cohort.csv",
            "--notice-assignments", "a.json",
            "--templates", str(TEMPLATES_DIR),
            "--config", str(CONFIG_DIR),
            "--output", str(OUTPUT_DIR),
        ]
    ]


def test_single_template_omits_templates_directory(fake_immuknow):
    calls, _ = fake_immuknow
    template = str(TEMPLATES_DIR / "overdue_diseases_v1.en.typ")
    run.main(["cohort.csv", "--template", template])
    assert "--templates" not in calls[0]
    assert calls[0][2:4] == ["--template", template]


def test_other_options_pass_through(fake_immuknow):
    calls, _ = fake_immuknow
    run.main(["cohort.csv", "--notice-assignments", "a.json", "--input-encoding", "cp1252"])
    assert calls[0][-2:] == ["--input-encoding", "cp1252"]


def test_exit_code_comes_from_immuknow(fake_immuknow):
    _, result = fake_immuknow
    result["returncode"] = 1
    assert run.main(["cohort.csv", "--notice-assignments", "a.json"]) == 1


def test_warnings_print_review_instructions(fake_immuknow, tmp_path, capsys):
    _, result = fake_immuknow
    result["status"] = "completed_with_warnings"
    run.main(["cohort.csv", "--notice-assignments", "a.json", "--output", str(tmp_path / "out")])
    assert "immuknow-rebundle" in capsys.readouterr().out


def test_bare_template_name_is_in_templates(fake_immuknow):
    calls, _ = fake_immuknow
    run.main(["cohort.csv", "--template", "overdue_diseases_v1.en.typ"])
    assert calls[0][2:4] == ["--template", str(TEMPLATES_DIR / "overdue_diseases_v1.en.typ")]


def test_templates_with_template_is_an_error(fake_immuknow, capsys):
    calls, _ = fake_immuknow
    with pytest.raises(SystemExit):
        run.main(["cohort.csv", "--template", "a.en.typ", "--templates", "elsewhere"])
    assert calls == []
    assert "--templates cannot be used with --template" in capsys.readouterr().err


def test_unreadable_run_record_is_explained(fake_immuknow, tmp_path, capsys):
    _, result = fake_immuknow
    result["status"] = "completed"
    run.main(["cohort.csv", "--notice-assignments", "a.json", "--output", str(tmp_path / "out")])
    (record,) = (tmp_path / "out").glob("*/run.json")
    record.write_text("{", encoding="utf-8")
    run.print_outcome(record.parent)
    assert "Could not read the run record" in capsys.readouterr().err


def test_quiet_run_hides_immuknow_output_and_review_hint(fake_immuknow, tmp_path, capsys):
    _, result = fake_immuknow
    result["status"] = "completed_with_warnings"
    run.main(
        ["cohort.csv", "--notice-assignments", "a.json", "--output", str(tmp_path / "out")],
        quiet=True,
    )
    assert capsys.readouterr().out == ""


def test_sample_uses_project_selection(fake_immuknow):
    from project import SAMPLE_ASSIGNMENTS, SAMPLE_INPUT

    calls, _ = fake_immuknow
    assert run.main(["--sample"]) == 0
    assert calls[0][1:4] == [str(SAMPLE_INPUT), "--notice-assignments", str(SAMPLE_ASSIGNMENTS)]


def test_concurrent_runs_are_not_misattributed(monkeypatch, tmp_path, capsys):
    def concurrent_run(command, **kwargs):
        for name, status in [("own", "completed"), ("other", "failed_setup")]:
            directory = tmp_path / name
            directory.mkdir()
            (directory / "run.json").write_text(json.dumps({"status": status}))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(run, "immuknow_command", lambda: "immuknow")
    monkeypatch.setattr(run.subprocess, "run", concurrent_run)
    assert run.main(["cohort.csv", "--template", "notice.en.typ", "--output", str(tmp_path)]) == 0
    captured = capsys.readouterr()
    assert "Run status:" not in captured.out
    assert "Several runs appeared" in captured.err
