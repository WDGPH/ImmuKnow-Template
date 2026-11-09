"""Maintained starters retain their wording, language and page choices."""

import pytest
from pypdf import PdfReader

pytestmark = pytest.mark.pipeline


def test_sample_starters_have_expected_titles_and_pages(sample_run):
    _, directory, record = sample_run
    entries = record["entries"]
    for entry in entries:
        reader = PdfReader(directory / entry["original"]["path"])
        first = " ".join(reader.pages[0].extract_text().split())
        language = entry["assignment"]["language"]
        title = (
            "Demande de dossier d'immunisation"
            if language == "fr"
            else "Request for Immunization Record"
        )
        assert title in first
        assert entry["client_id"] in first
        assert (
            "15 novembre 2026" if language == "fr" else "November 15, 2026"
        ) in first
        assert reader.root_object["/Lang"] == f"{language}-CA"
        assert len(reader.pages) == 2
        assert all(
            "MARK_END_" not in page.extract_text()
            and "MEASURE_" not in page.extract_text()
            for page in reader.pages
        )


def test_sample_selects_expected_starter_content(sample_run):
    _, directory, record = sample_run
    entries = record["entries"]

    def first_page(entry):
        reader = PdfReader(directory / entry["original"]["path"])
        return " ".join(reader.pages[0].extract_text().split())

    def child(entry):
        return entry["notice"]["intended_reader"] == "guardian" or (
            entry["notice"]["intended_reader"] is None
            and entry["notice"]["client_data"]["age"] < 16
        )

    overdue = next(
        e
        for e in entries
        if e["assignment"]["language"] == "en"
        and e["assignment"]["notice_kind"] == "overdue"
        and child(e)
    )
    affirmative = next(
        e
        for e in entries
        if e["assignment"]["language"] == "en"
        and e["assignment"]["notice_kind"] == "affirmative"
        and child(e)
    )
    french = next(
        e for e in entries if e["assignment"]["language"] == "fr" and child(e)
    )
    assert "your child has" in first_page(overdue)
    assert "your child is" in first_page(affirmative)
    assert "votre enfant" in first_page(french)


def test_suspension_starter_has_its_own_title_and_one_page(tmp_path):
    import csv
    import json

    import run
    from project import SAMPLE_INPUT, TEMPLATES_DIR

    with SAMPLE_INPUT.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fieldnames = reader.fieldnames
        row = next(reader)
    csv_path = tmp_path / "one-client.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)
    output = tmp_path / "runs"
    code = run.main(
        [
            str(csv_path),
            "--template",
            str(TEMPLATES_DIR / "suspension_order.en.typ"),
            "--output",
            str(output),
        ]
    )
    (record_path,) = output.glob("*/run.json")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    entry = record["entries"][0]
    assert code == 0, record["status"]
    pdf = PdfReader(record_path.parent / entry["original"]["path"])
    assert len(pdf.pages) == 1
    text = " ".join(pdf.pages[0].extract_text().split())
    assert "Order for Suspension from Attendance at School" in text
    assert "twenty school days" in text
    assert "Suspension begins: December 1, 2026" in text
    assert "February 2, 2026" not in text
    assert "March 2, 2026" not in text


def test_starter_excludes_recommendation_agents_but_preserves_source_facts(tmp_path):
    import csv
    import json

    import run
    from project import SAMPLE_INPUT, TEMPLATES_DIR

    with SAMPLE_INPUT.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fieldnames = reader.fieldnames
        row = next(reader)
    excluded = ["COVID-19 mRNA", "Inf (TIV)"]
    row["overdue_agent"] += ";".join(excluded) + ";"
    csv_path = tmp_path / "one-client.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)
    output = tmp_path / "runs"
    code = run.main(
        [
            str(csv_path),
            "--template",
            str(TEMPLATES_DIR / "overdue_agents.en.typ"),
            "--output",
            str(output),
        ]
    )
    (record_path,) = output.glob("*/run.json")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert code == 0, record["status"]
    entry = record["entries"][0]
    assert all(agent in entry["notice"]["overdue_agents"] for agent in excluded)
    assert entry["source"]["overdue_agent"] == row["overdue_agent"]
    pdf = PdfReader(record_path.parent / entry["original"]["path"])
    text = " ".join(pdf.pages[0].extract_text().split())
    assert "DTaP-IPV-Hib" in text
    assert all(agent not in text for agent in excluded)
