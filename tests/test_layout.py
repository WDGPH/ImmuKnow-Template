"""The project contains what ImmuKnow reads from config/ and templates/."""

import json

import pytest

from check import catalog_entry_points
from project import CONFIG_DIR, SAMPLE_ASSIGNMENTS, SAMPLE_INPUT, TEMPLATES_DIR


@pytest.mark.parametrize(
    "name",
    [
        "parameters.yaml",
        "notice_versions.yaml",
        "vaccine_reference.json",
        "disease_normalization.json",
    ],
)
def test_config_file_present(name):
    assert (CONFIG_DIR / name).is_file()


@pytest.mark.parametrize("name", ["settings.typ", "presentation.typ"])
def test_template_support_file_present(name):
    assert (TEMPLATES_DIR / name).is_file()


def test_project_has_catalog_notice_entry_points():
    entry_points = catalog_entry_points(CONFIG_DIR, TEMPLATES_DIR)
    assert entry_points
    assert [version for version, languages in entry_points.items() if not languages] == []


def test_sample_assignments_name_existing_templates():
    assignments = json.loads(SAMPLE_ASSIGNMENTS.read_text(encoding="utf-8"))
    missing = {a["template"] for a in assignments} - {
        path.name for path in TEMPLATES_DIR.glob("*.typ")
    }
    assert missing == set()


def test_sample_assignments_cover_sample_clients():
    import csv

    with SAMPLE_INPUT.open(encoding="utf-8-sig", newline="") as source:
        clients = {row["client_id"] for row in csv.DictReader(source)}
    assignments = json.loads(SAMPLE_ASSIGNMENTS.read_text(encoding="utf-8"))
    assert [a["client_id"] for a in assignments] == sorted(clients)
