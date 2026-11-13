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
        assert len(reader.pages) == (3 if entry["client_id"] == "9848574731" else 2)
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
        and e["assignment"]["version_id"] in {"overdue_agents", "overdue_diseases"}
        and child(e)
    )
    affirmative = next(
        e
        for e in entries
        if e["assignment"]["language"] == "en"
        and e["assignment"]["version_id"] == "affirmative_schedule"
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
    excluded = ["COVID-19 mRNA", "Inf (TIV)", "TIg"]
    row["overdue_disease"] += "Meningococcal disease;"
    row["overdue_agent"] += ";".join(["Men-C-ACYW-135", *excluded]) + ";"
    row["immunizations_given"] += " 2020-01-13 - TIg - Valid;"
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
    assert entry["source"]["immunizations_given"] == row["immunizations_given"]
    coverage = next(c for c in entry["checks"] if c["code"] == "data.forecast_coverage")
    assert coverage["measurements"]["missing_diseases"] == []
    assert coverage["measurements"]["unmapped_agents"] == []
    pdf = PdfReader(record_path.parent / entry["original"]["path"])
    text = " ".join(pdf.pages[0].extract_text().split())
    assert "DTaP-IPV-Hib" in text
    assert "Men-C-ACYW-135" in text
    assert all(agent not in text for agent in excluded)
    history = " ".join(pdf.pages[1].extract_text().split())
    assert "2020-01-13" not in history


@pytest.mark.parametrize(
    (
        "template",
        "diseases",
        "agents",
        "history",
        "check",
        "status",
        "routing",
        "wording",
    ),
    [
        (
            "affirmative_schedule",
            "Diphtheria;",
            "DTaP-IPV-Hib;",
            "keep",
            "notice.eligibility",
            "fail",
            "review",
            "up-to-date",
        ),
        (
            "suspension_order",
            "",
            "",
            "keep",
            "notice.eligibility",
            "fail",
            "review",
            "Order for Suspension",
        ),
        (
            "overdue_agents",
            "Diphtheria;",
            "Var;",
            "keep",
            "data.forecast_coverage",
            "fail",
            "review",
            "Var",
        ),
        (
            "overdue_diseases",
            "Diphtheria;",
            "Var;",
            "keep",
            "data.forecast_coverage",
            "warn",
            None,
            "Diphtheria",
        ),
        (
            "overdue_agents",
            "Diphtheria;",
            "COVID-19 mRNA; Inf (TIV); TIg;",
            "keep",
            "content.agent_display",
            "fail",
            "review",
            "Request for Immunization Record",
        ),
        (
            "overdue_agents",
            "Diphtheria;",
            "COVID-19 mRNA; Inf (TIV); TIg;",
            "",
            "content.agent_display",
            "pass",
            None,
            "We have no immunization records on file",
        ),
    ],
)
def test_starter_requirements_and_display_keep_readable_notices(
    tmp_path, template, diseases, agents, history, check, status, routing, wording
):
    import csv
    import json

    import run
    from project import SAMPLE_INPUT, TEMPLATES_DIR

    with SAMPLE_INPUT.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fieldnames = reader.fieldnames
        row = next(reader)
    row["overdue_disease"] = diseases
    row["overdue_agent"] = agents
    if history != "keep":
        row["immunizations_given"] = history
    csv_path = tmp_path / "one-client.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)
    output = tmp_path / "runs"
    run.main(
        [
            str(csv_path),
            "--template",
            str(TEMPLATES_DIR / f"{template}.en.typ"),
            "--output",
            str(output),
        ]
    )
    (record_path,) = output.glob("*/run.json")
    entry = json.loads(record_path.read_text(encoding="utf-8"))["entries"][0]
    assert next(c for c in entry["checks"] if c["code"] == check)["status"] == status
    if routing is not None:
        assert entry["routing"] == routing
    assert entry["source"]["overdue_agent"] == agents
    pdf = PdfReader(record_path.parent / entry["original"]["path"])
    assert wording in " ".join(pdf.pages[0].extract_text().split())


def test_bilingual_variants_keep_long_history_and_qr_evidence(tmp_path):
    import csv
    import datetime
    import json

    import run
    from project import SAMPLE_ASSIGNMENTS, SAMPLE_INPUT

    with SAMPLE_INPUT.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames
        sample = {row["client_id"]: row for row in reader}
    assignments = json.loads(SAMPLE_ASSIGNMENTS.read_text())
    agents = ["MMR", "DTaP-IPV", "Hib", "Men-C-C", "Pneu-C-13"]
    history = " ".join(
        f"{(datetime.date(2015, 1, 1) + datetime.timedelta(days=i * 50)).isoformat()} - {agents[i % len(agents)]} - Valid;"
        for i in range(50)
    )
    rows = []
    selected = []
    for language in ("en", "fr"):
        for variant in ("overdue_agents", "overdue_diseases"):
            original = next(
                item
                for item in assignments
                if item["template"] == f"{variant}.{language}.typ"
            )
            row = sample[original["client_id"]].copy()
            row["client_id"] = f"{2000000001 + len(rows):010}"
            row["first_name"] = (
                "Éléonore-Camille" if language == "fr" else "Alexandrine-Marie"
            )
            row["last_name"] = (
                "Deschamps-Lefrançois"
                if language == "fr"
                else "Fictional-Sample-Longname"
            )
            row["street_address_line_1"] = "12345 Long Fictional Avenue"
            row["street_address_line_2"] = "Apartment 123, Building North"
            row["immunizations_given"] = history
            rows.append(row)
            selected.append(
                {"client_id": row["client_id"], "template": original["template"]}
            )
    source = tmp_path / "long-fictional.csv"
    with source.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    manifest = tmp_path / "assignments.json"
    manifest.write_text(json.dumps(selected))
    output = tmp_path / "runs"
    code = run.main(
        [str(source), "--notice-assignments", str(manifest), "--output", str(output)]
    )
    (record_path,) = output.glob("*/run.json")
    record = json.loads(record_path.read_text())
    assert code == 0, record["status"]
    assert len(record["entries"]) == 4
    for entry in record["entries"]:
        assert len(entry["notice"]["history"]) == 50
        assert (
            entry["saved_evidence"]["measurements"]["history"][0]["displayed_rows"]
            == 50
        )
        assert len(entry["saved_evidence"]["qr_urls"]) == 1
        pdf = PdfReader(record_path.parent / entry["original"]["path"])
        assert len(pdf.pages) >= 3
        assert pdf.root_object["/Lang"] == f"{entry['assignment']['language']}-CA"
        assert entry["client_id"] in " ".join(pdf.pages[0].extract_text().split())
