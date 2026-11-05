"""Starter wording, language and page choices belong to Template."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from pypdf import PdfReader

from immuknow.data_models import ClientRecord
from immuknow.compile_notices import compile_render_job
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
                "mapping_known": True,
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
    diagnostics, report, error = compile_render_job(job, native)
    assert not diagnostics
    assert error is None
    assert report is not None
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


@pytest.mark.parametrize("age", [15, 16, None])
@pytest.mark.parametrize("intended_reader", [None, "student", "guardian"])
def test_reader_flags_select_wording_and_the_same_addressee(
    tmp_path, age, intended_reader
):
    job, payload = prepare_case(tmp_path, "overdue_diseases_v1", "en")
    payload["client_data"]["age"] = age
    payload["intended_reader"] = intended_reader
    job.data.write_text(json.dumps(payload))
    job.template.write_text(
        job.template.read_text()
        + "\n#assert(type(to_student) == bool and type(to_guardian) == bool)\n"
        "#assert(not (to_student and to_guardian))\n"
    )
    selected = intended_reader or (
        None if age is None else "student" if age >= 16 else "guardian"
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
    assert report["notice"]["client_data"]["age"] == age


@pytest.mark.parametrize(
    "age,intended_reader,service,heading",
    [
        (16, "guardian", "Serve: Parent/Guardian.", "Parent/Guardian:"),
        (15, "student", "Serve: Parent/Guardian and student.", "Student:"),
        (None, None, "Serve: Client or representative.", "Client or representative:"),
    ],
)
def test_suspension_uses_the_selected_reader_throughout(
    tmp_path, age, intended_reader, service, heading
):
    job, payload = prepare_case(tmp_path, "suspension_order_v1", "en")
    payload["client_data"]["age"] = age
    payload["intended_reader"] = intended_reader
    job.data.write_text(json.dumps(payload))
    report, pdf = compile_case(job)
    text = " ".join(pdf.pages[0].extract_text().split())
    assert len(pdf.pages) == 1
    assert service in text
    assert heading in text
    label = "To Parent/Guardian of:" if intended_reader == "guardian" else "To:"
    assert report["measurements"]["address"][0]["text"].startswith(label)


@pytest.mark.parametrize("kind", ["diseases", "agents"])
@pytest.mark.parametrize("language", ["en", "fr"])
def test_no_record_starters_request_records_without_claiming_no_vaccines(
    tmp_path, kind, language
):
    job, payload = prepare_case(tmp_path, f"overdue_{kind}_v1", language)
    payload.update(
        history=[],
        has_immunization_records=False,
        history_validity_coverage="all_absent",
    )
    job.data.write_text(json.dumps(payload))
    report, pdf = compile_case(job)
    first = " ".join(pdf.pages[0].extract_text().split())
    assert (
        "We have no immunization records on file"
        if language == "en"
        else "Aucune vaccination n’est consignée au dossier"
    ) in first
    assert (
        "not received the following"
        if language == "en"
        else "pas reçu les immunisations suivantes"
    ) not in first
    assert len(pdf.pages) == 2
    assert report["components"][f"overdue_{kind}"]


def test_affirmative_starter_rejects_overdue_diseases(tmp_path):
    job, payload = prepare_case(tmp_path, "affirmative_schedule_v1", "en")
    payload["overdue_diseases"] = [{"disease": "Measles", "dose": 2}]
    job.data.write_text(json.dumps(payload))
    with pytest.raises(subprocess.CalledProcessError) as failure:
        compile_case(job)
    assert "affirmative notice requires no overdue diseases" in failure.value.stderr


@pytest.mark.parametrize(
    "birth,diseases,allowed",
    [
        ("2010-01-01", ["Varicella", "Hib"], True),
        ("2009-12-31", ["Varicella", "Hib"], False),
        ("2009-12-31", ["Measles", "Hib"], True),
    ],
)
def test_suspension_starter_requires_and_names_only_cohort_ispa_diseases(
    tmp_path, birth, diseases, allowed
):
    job, payload = prepare_case(tmp_path, "suspension_order_v1", "en")
    payload["client_data"]["date_of_birth_iso"] = birth
    payload["overdue_diseases"] = [
        {"disease": disease, "dose": 1} for disease in diseases
    ]
    job.data.write_text(json.dumps(payload))
    if not allowed:
        with pytest.raises(subprocess.CalledProcessError) as failure:
            compile_case(job)
        assert (
            "suspension notice requires an overdue ISPA disease" in failure.value.stderr
        )
        return
    _, pdf = compile_case(job)
    first = " ".join(pdf.pages[0].extract_text().split())
    assert diseases[0] in first
    assert "Haemophilus" not in first and "Hib" not in first
    assert len(pdf.pages) == 1


@pytest.mark.parametrize("language", ["en", "fr"])
def test_settings_bind_identifier_options_and_bilingual_missing_text(
    tmp_path, language
):
    job, payload = prepare_case(tmp_path, "overdue_diseases_v1", language)
    payload.update(oiid="", oiid_coverage="mixed")
    job.data.write_text(json.dumps(payload))
    settings = job.template.parent / "settings.typ"
    settings.write_text(
        settings.read_text()
        .replace("show-client-id: true", "show-client-id: false")
        .replace("show-oiid: false", "show-oiid: true")
        .replace("missing-oiid: none", "missing-oiid: auto")
    )
    report, pdf = compile_case(job)
    first = " ".join(pdf.pages[0].extract_text().split())
    assert ("Not available" if language == "en" else "Non disponible") in first
    assert payload["client_id"] not in first
    assert report["identity"]["client_id"] == payload["client_id"]


@pytest.mark.parametrize("language", ["en", "fr"])
def test_history_starter_defaults_show_validity_and_allow_legend_wording(
    tmp_path, language
):
    job, payload = prepare_case(tmp_path, "overdue_diseases_v1", language)
    payload["history"][0]["validity"] = "invalid"
    payload.update(
        validity_coverage="all_present", history_validity_coverage="all_present"
    )
    job.data.write_text(json.dumps(payload))
    settings = job.template.parent / "settings.typ"
    settings.write_text(
        settings.read_text().replace(
            "legend-labels: (:)", 'legend-labels: (invalid: "Custom dose explanation")'
        )
    )
    _, pdf = compile_case(job)
    last = " ".join(pdf.pages[-1].extract_text().split())
    assert "Custom dose explanation" in last
    assert (
        "Unspecified vaccine" if language == "en" else "Vaccin non précisé"
    ) not in last
