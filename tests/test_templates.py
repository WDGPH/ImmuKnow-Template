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
