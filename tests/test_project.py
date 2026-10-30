"""Sample selection stays within the extracted project."""

import json

import pytest

import project


def test_studio_sample_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(project, "ROOT", tmp_path)
    (tmp_path / "sample.json").write_text(
        json.dumps(
            {
                "csv": "examples/clients/short.fr.csv",
                "assignments": "examples/assignments/short.notice.fr.json",
            }
        )
    )
    assert project.sample_paths() == (
        tmp_path / "examples/clients/short.fr.csv",
        tmp_path / "examples/assignments/short.notice.fr.json",
    )


@pytest.mark.parametrize("path", ["../cohort.csv", "/cohort.csv", "..\\cohort.csv", ""])
def test_sample_cannot_escape_project(monkeypatch, tmp_path, path):
    monkeypatch.setattr(project, "ROOT", tmp_path)
    (tmp_path / "sample.json").write_text(
        json.dumps({"csv": path, "assignments": "a.json"})
    )
    with pytest.raises(ValueError, match="relative path"):
        project.sample_paths()
