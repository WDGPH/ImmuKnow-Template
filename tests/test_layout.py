"""The project contains what ImmuKnow reads from config/ and templates/."""

import json

import pytest

from support import CONFIG_DIR, SAMPLE_ASSIGNMENTS, SAMPLE_INPUT, TEMPLATES_DIR


@pytest.mark.parametrize(
    "name",
    [
        "parameters.yaml",
        "vaccine_reference.json",
        "disease_normalization.json",
    ],
)
def test_config_file_present(name):
    assert (CONFIG_DIR / name).is_file()


def test_notice_catalog_is_absent():
    assert not (CONFIG_DIR / "notice_versions.yaml").exists()


def test_settings_contains_explicit_translation_dependencies():
    source = (TEMPLATES_DIR / "settings.typ").read_text(encoding="utf-8")
    for language in ("en", "fr"):
        for kind in ("chart", "overdue"):
            name = f"translations/{language}_diseases_{kind}.json"
            assert f'json("{name}")' in source
            assert (TEMPLATES_DIR / name).is_file()
    assert not (TEMPLATES_DIR / "setup.typ").exists()
    assert not (TEMPLATES_DIR / "presentation.typ").exists()


def test_project_has_maintained_notice_entry_points():
    for name in (
        "overdue_diseases.en.typ",
        "overdue_diseases.fr.typ",
        "overdue_agents.en.typ",
        "overdue_agents.fr.typ",
        "affirmative_schedule.en.typ",
        "suspension_order.en.typ",
    ):
        source = (TEMPLATES_DIR / name).read_text(encoding="utf-8")
        assert '#import "settings.typ" as immuknow' in source
        assert "#show: immuknow.letter" in source


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
    assigned = [a["client_id"] for a in assignments]
    assert len(assigned) == len(set(assigned))
    assert set(assigned) == clients
