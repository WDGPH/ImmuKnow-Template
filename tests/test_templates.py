"""Starter wording, language and page choices belong to Template."""

import json
import os
import shutil
from pathlib import Path

import pytest
import yaml
from pypdf import PdfReader

from immuknow.data_models import ClientRecord
from immuknow.compile_notices import compile_render_job, evaluate_render_job
from immuknow.generate_notices import prepare_render_jobs
from project import CONFIG_DIR, TEMPLATES_DIR

pytestmark = pytest.mark.pipeline


def prepare_case(workspace, version, language):
    shutil.copytree(TEMPLATES_DIR, workspace / "resources/templates")
    client = ClientRecord(
        sequence="row-000001",
        client_id="0000000001",
        language=language,
        version_id=version,
        person={
            "first_name": "Alice",
            "last_name": "Zephyr",
            "date_of_birth_iso": "2015-01-02",
            "age": 9,
            "over_16": False,
        },
        contact={
            "street": "123 Main St",
            "city": "Guelph",
            "province": "ON",
            "postal_code": "N1H 2T2",
        },
        school={"id": "school-1", "name": "Tunnel Academy"},
        board={"id": "board-1", "name": "Example Board"},
        overdue_diseases=[]
        if version == "affirmative_schedule_v1"
        else [{"disease": "Measles", "dose": 2}],
        overdue_agents=[] if version == "affirmative_schedule_v1" else ["MMR", "DTaP"],
        history=[
            {
                "date_given": "2020-05-01",
                "diseases": ["Diphtheria", "Tetanus", "Pertussis"],
                "agent": "DTaP",
                "display_name": "DTaP",
                "validity": "unknown",
            }
        ],
        metadata={},
    )
    config = yaml.safe_load((CONFIG_DIR / "parameters.yaml").read_text())
    config["creation_timestamp"] = 1780272000
    job = prepare_render_jobs([client], workspace, config)[0]
    return job, json.loads(job.data.read_text())


def compile_case(job):
    native = os.environ.get("TYPST_BIN", "typst")
    assert not compile_render_job(job, native)
    report = evaluate_render_job(job, native)
    return report, PdfReader(job.pdf)


@pytest.mark.parametrize(
    "version,language,title,selected_wording,pages",
    [
        (
            "overdue_diseases_v1",
            "en",
            "Request for Immunization Record",
            "your child has",
            2,
        ),
        (
            "overdue_diseases_v1",
            "fr",
            "Demande de dossier d'immunisation",
            "votre enfant n’a",
            2,
        ),
        (
            "overdue_agents_v1",
            "en",
            "Request for Immunization Record",
            "your child has",
            2,
        ),
        (
            "overdue_agents_v1",
            "fr",
            "Demande de dossier d'immunisation",
            "votre enfant n’a",
            2,
        ),
        (
            "affirmative_schedule_v1",
            "en",
            "Request for Immunization Record",
            "your child is",
            2,
        ),
        (
            "suspension_order_v1",
            "en",
            "Order for Suspension from Attendance at School",
            "twenty school days",
            1,
        ),
    ],
)
def test_maintained_entry_points_keep_their_content_and_component_choices(
    tmp_path: Path,
    version: str,
    language: str,
    title: str,
    selected_wording: str,
    pages: int,
):
    job, _ = prepare_case(tmp_path, version, language)
    report, reader = compile_case(job)
    first = " ".join(reader.pages[0].extract_text().split())
    assert title in first
    assert selected_wording in first
    assert "0000000001" in first
    assert reader.root_object["/Lang"] == language + "-CA"
    assert len(reader.pages) == pages
    assert report["identity"] == {
        "row_key": job.sequence,
        "template": job.template.name,
        "client_id": "0000000001",
        "version_id": version,
        "language": language,
    }
    assert job.template.read_bytes() == (TEMPLATES_DIR / job.template.name).read_bytes()
    assert not any(
        "MARK_END_" in page.extract_text() or "MEASURE_" in page.extract_text()
        for page in reader.pages
    )
    suspension = version == "suspension_order_v1"
    assert report["components"]["qr"] is (
        not suspension and version != "affirmative_schedule_v1"
    )
    assert report["components"]["history"] is (not suspension)
    assert report["components"]["privacy"] is (not suspension)
    privacy_text = (
        "The information in this notice was collected"
        if language == "en"
        else "Les renseignements figurant dans cet avis"
    )
    assert privacy_text not in first
    if not suspension:
        last = " ".join(reader.pages[-1].extract_text().split())
        assert privacy_text in last
        assert report["measurements"]["privacy"] == [{"page": pages}]
        assert any(
            check["code"] == "layout.privacy_page" and check["status"] == "pass"
            for check in report["checks"]
        )
        assert "2020-05-01" in last and "DTaP" in last
        assert (
            "End of immunization record"
            if language == "en"
            else "Fin du dossier d’immunisation"
        ) in last
    if version == "overdue_agents_v1":
        assert "MMR" in first and "DTaP" in first
        assert ("• Measles" if language == "en" else "• Rougeole") not in first
    elif version == "overdue_diseases_v1":
        assert ("Measles" if language == "en" else "Rougeole") in first


def test_local_history_and_page_options_preserve_project_defaults(tmp_path):
    job, _ = prepare_case(tmp_path, "overdue_diseases_v1", "en")
    job.template.write_text(
        '#import "setup.typ": *\n#show: immuknow.letter\n'
        '#immuknow.notice-page("Default before")[#immuknow.immunization-history()]\n'
        '#immuknow.notice-page("Local choices", title-size: 16pt)[\n'
        "#immuknow.immunization-history(show-age: true, font-size: 12pt, min-rows: 8)\n]\n"
        '#immuknow.notice-page("Default after")[#immuknow.immunization-history()]\n'
    )
    report, reader = compile_case(job)
    assert len(reader.pages) == 3
    assert len(report["measurements"]["history"]) == 3
    spans = []
    for page in reader.pages:
        values = []
        page.extract_text(
            visitor_text=lambda text, _cm, _tm, _font, size: values.append(
                (text.strip(), size)
            )
        )
        spans.append(values)
    for index in (0, 2):
        assert not any(" yr " in text for text, _ in spans[index])
        assert any("2020-05-01" in text and size == 11 for text, size in spans[index])
    assert any(" yr " in text for text, _ in spans[1])
    assert any("2020-05-01" in text and size == 12 for text, size in spans[1])
    assert ("Local choices", 16) in spans[1]
    assert ("Default before", 20) in spans[0]
    assert ("Default after", 20) in spans[2]


def test_setup_namespace_supplies_client_data_and_keeps_general_helpers(tmp_path):
    job, _ = prepare_case(tmp_path, "overdue_diseases_v1", "en")
    job.template.write_text(
        '#import "setup.typ": *\n'
        "#show: immuknow.letter\n"
        '#immuknow.check-notice(version: "overdue_diseases_v1", language: "en")\n'
        "#immuknow.notice-dates().date_as_of\n"
        "#immuknow.address-block()\n"
        "#immuknow.overdue-agents(columns: 1)\n"
        '#immuknow.link("mailto:records@example.org")\n'
        "#link(<details>)[Details]\n= Details <details>\n"
        '#immuknow.qr-code(url: n => immuknow.query-url("https://example.org", (id: n.client_id)))\n'
        '#immuknow.qr-code(enabled: false, url: n => panic("Unused QR destination"))\n'
    )
    report, reader = compile_case(job)
    text = " ".join(page.extract_text() for page in reader.pages)
    assert "Alice Zephyr" in text
    assert "MMR" in text and "DTaP" in text
    assert report["qr_urls"] == ["https://example.org?id=0000000001"]
    for component in ("address", "overdue_agents", "qr"):
        assert report["components"][component]
        assert all(item["source_matches"] for item in report["measurements"][component])
    assert not report["components"]["history"]


def test_unused_history_defaults_are_not_evaluated(tmp_path):
    job, _ = prepare_case(tmp_path, "suspension_order_v1", "en")
    settings = job.template.parent / "settings.typ"
    settings.write_text(settings.read_text().replace("min-rows: 5", "min-rows: -1"))
    report, _ = compile_case(job)
    assert not report["components"]["history"]


@pytest.mark.parametrize("over_16", [True, False, None])
@pytest.mark.parametrize("reader", [None, "student", "guardian"])
def test_reader_flags_select_wording_and_the_same_addressee(tmp_path, over_16, reader):
    job, payload = prepare_case(tmp_path, "overdue_diseases_v1", "en")
    payload["client_data"]["over_16"] = over_16
    payload["reader"] = reader
    job.data.write_text(json.dumps(payload))
    job.template.write_text(
        job.template.read_text()
        + "\n#assert(type(to_student) == bool and type(to_guardian) == bool)\n"
        "#assert(not (to_student and to_guardian))\n"
    )
    selected = reader or (
        None if over_16 is None else "student" if over_16 else "guardian"
    )
    report, pdf = compile_case(job)
    text = " ".join(pdf.pages[0].extract_text().split())
    wording = {
        "student": "you have",
        "guardian": "your child has",
        None: "the named client has",
    }[selected]
    assert wording in text
    label = "To Parent/Guardian of:" if selected == "guardian" else "To:"
    assert report["measurements"]["address"][0]["text"].startswith(label)
    assert report["notice"]["client_data"]["over_16"] is over_16


@pytest.mark.parametrize(
    "over_16,reader,service,heading",
    [
        (True, "guardian", "Serve: Parent/Guardian.", "Parent/Guardian:"),
        (False, "student", "Serve: Parent/Guardian and student.", "Student:"),
        (None, None, "Serve: Client or representative.", "Client or representative:"),
    ],
)
def test_suspension_uses_the_selected_reader_throughout(
    tmp_path, over_16, reader, service, heading
):
    job, payload = prepare_case(tmp_path, "suspension_order_v1", "en")
    payload["client_data"]["over_16"] = over_16
    payload["reader"] = reader
    job.data.write_text(json.dumps(payload))
    report, pdf = compile_case(job)
    text = " ".join(pdf.pages[0].extract_text().split())
    assert len(pdf.pages) == 1
    assert service in text
    assert heading in text
    label = "To Parent/Guardian of:" if reader == "guardian" else "To:"
    assert report["measurements"]["address"][0]["text"].startswith(label)
