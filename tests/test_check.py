"""check.py summarizes sample findings by code instead of linking a deleted report."""

from check import finding_summary


def entry(*checks):
    return {"checks": [{"code": code, "status": status} for code, status in checks]}


def test_findings_are_grouped_by_code_with_failures_first():
    record = {
        "entries": [
            entry(("content.multiple_links", "warn"), ("layout.fits", "pass")),
            entry(("content.multiple_links", "warn"), ("output.identity", "fail")),
            entry(("source.address_incomplete", "warn"), ("qr.absent", "not_applicable")),
        ],
        "checks": [],
    }
    assert finding_summary(record) == [
        "fail  output.identity: 1 notice",
        "warn  content.multiple_links: 2 notices",
        "warn  source.address_incomplete: 1 notice",
    ]


def test_repeated_code_on_one_notice_counts_once():
    record = {
        "entries": [entry(("data.history", "warn"), ("data.history", "warn"))],
        "checks": [],
    }
    assert finding_summary(record) == ["warn  data.history: 1 notice"]


def test_run_level_failure_shows_its_message():
    record = {
        "entries": [],
        "checks": [{"code": "run.failed", "status": "fail", "message": "Typst not found"}],
    }
    assert finding_summary(record) == ["fail  run.failed: Typst not found"]


def test_clean_run_has_no_summary():
    assert finding_summary({"entries": [entry(("layout.fits", "pass"))], "checks": []}) == []
