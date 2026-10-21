"""check_client_data.py refuses files that may hold client information."""

from check_client_data import client_data


def test_client_data_files_are_found():
    assert client_data(
        [
            "students.CSV",
            "notes/run.json",
            "runs/2026/report.html",
            "export.xlsx",
            "input/assignments.json",
            "input/sample/real_cohort.json",
            "output/old/notice.typ",
        ]
    ) == [
        "students.CSV",
        "notes/run.json",
        "runs/2026/report.html",
        "export.xlsx",
        "input/assignments.json",
        "input/sample/real_cohort.json",
        "output/old/notice.typ",
    ]


def test_project_files_and_sample_are_allowed():
    assert client_data(
        [
            "input/sample/rodent_dataset.csv",
            "input/sample/assignments.json",
            "config/vaccine_reference.json",
            "templates/assets/logo.png",
            "README.md",
        ]
    ) == []
