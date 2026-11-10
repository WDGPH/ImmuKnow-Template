"""Check that this machine and project are ready to run ImmuKnow.

Usage
-----
    python scripts/check.py           # setup checks
    python scripts/check.py --sample  # also run the sample end to end

Checks compare the shared Typst library and ask the standalone executable to
prepare the sample. --sample also compiles the notices and reports findings.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import run
from project import (
    CONFIG_DIR,
    LIBRARY,
    SAMPLE_ASSIGNMENTS,
    SAMPLE_INPUT,
    TEMPLATES_DIR,
    immuknow_command,
)
from sync_lib import ensure_library


def prepare_sample() -> dict:
    """Ask the standalone executable to validate inputs without making PDFs."""
    result = subprocess.run(
        [
            immuknow_command(),
            "prepare",
            str(SAMPLE_INPUT),
            "--notice-assignments",
            str(SAMPLE_ASSIGNMENTS),
            "--templates",
            str(TEMPLATES_DIR),
            "--config",
            str(CONFIG_DIR),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise ValueError(result.stderr.strip() or "ImmuKnow preparation failed")
    try:
        prepared = json.loads(result.stdout)
    except ValueError as exc:
        raise ValueError("ImmuKnow returned invalid preparation JSON") from exc
    if (
        not isinstance(prepared, dict)
        or prepared.get("schema_version") != 2
        or not isinstance(prepared.get("entries"), list)
    ):
        raise ValueError("ImmuKnow returned an unsupported preparation record")
    if any(
        finding.get("status") == "fail"
        for entry in prepared["entries"]
        for finding in entry.get("checks", [])
    ):
        raise ValueError(
            "Sample preparation contains failed rows; inspect the source and run prepare for findings"
        )
    return prepared


def run_sample() -> tuple[int, dict | None]:
    """Run the sample into a temporary directory and return its run record."""
    with tempfile.TemporaryDirectory() as output:
        code = run.main(
            [
                str(SAMPLE_INPUT),
                "--notice-assignments",
                str(SAMPLE_ASSIGNMENTS),
                "--output",
                output,
            ],
            quiet=True,
        )
        records = list(Path(output).glob("*/run.json"))
        record = json.loads(records[0].read_text(encoding="utf-8")) if records else None
    return code, record


def finding_summary(record: dict) -> list[str]:
    """Summarize effective findings and errors that explain failed output."""
    if record.get("run_schema_version") != 2:
        raise ValueError("Unsupported saved-run version")
    notices: Counter[tuple[str, str]] = Counter()
    for entry in record["entries"]:
        observed = entry["checks"]
        if "effective_checks" not in entry:
            if record.get("status") not in ("running", "failed"):
                raise ValueError("Completed saved row is missing effective results")
            checks = observed
        else:
            by_key = {check["finding_key"]: check for check in observed}
            if len(by_key) != len(observed):
                raise ValueError("Duplicate observed finding key")
            results = entry["effective_checks"]
            keys = [result["finding_key"] for result in results]
            if len(keys) != len(set(keys)) or set(keys) != set(by_key):
                raise ValueError("Effective results do not match observed findings")
            checks = [
                dict(by_key[result["finding_key"]], status=result["status"])
                for result in results
            ]
        for status, code in {
            (check["status"], check["code"])
            for check in checks
            if check["status"] in ("warn", "fail")
        }:
            notices[status, code] += 1
    lines = [
        f"{status:<4}  {code}: {count} notice{'s' if count != 1 else ''}"
        for (status, code), count in sorted(
            notices.items(),
            key=lambda item: (item[0][0] != "fail", -item[1], item[0][1]),
        )
    ]
    lines += [
        f"{check['status']:<4}  {check['code']}: {check['message']}"
        for check in record["checks"]
        if check["status"] in ("warn", "fail")
    ]
    for entry in record["entries"]:
        row = entry.get("row_key", "unknown row")
        for field, label in (
            ("original", "original PDF"),
            ("encryption", "encrypted copy"),
        ):
            artifact = entry.get(field) or {}
            if artifact.get("error"):
                lines.append(f"fail  {row} {label}: {artifact['error']}")
    if record.get("error"):
        lines.append(f"fail  run: {record['error']}")
    return lines


class Report:
    def __init__(self) -> None:
        self.failed = False

    def line(self, status: str, label: str, detail: str = "") -> None:
        self.failed |= status == "FAIL"
        print(f"{status:<4}  {label}" + (f": {detail}" if detail else ""), flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check this ImmuKnow project.")
    parser.add_argument(
        "--sample", action="store_true", help="also run the sample end to end"
    )
    args = parser.parse_args(argv)
    report = Report()

    try:
        binary = immuknow_command()
        version = subprocess.run([binary, "--version"], capture_output=True, text=True)
        if version.returncode:
            raise ValueError(version.stderr.strip() or "Could not run ImmuKnow")
        report.line("OK", "ImmuKnow", version.stdout.strip())
        ensure_library(TEMPLATES_DIR)
        report.line(
            "OK", f"templates/{LIBRARY.as_posix()}", "matches installed ImmuKnow"
        )
        prepared = prepare_sample()
        report.line(
            "OK", "sample preparation", f"{len(prepared['entries'])} source rows"
        )
    except (OSError, RuntimeError, ValueError) as exc:
        report.line("FAIL", "project setup", str(exc))

    if args.sample:
        if report.failed:
            report.line("SKIP", "sample run", "fix the failures above first")
        elif not SAMPLE_INPUT.is_file() or not SAMPLE_ASSIGNMENTS.is_file():
            report.line(
                "FAIL",
                "sample run",
                "sample inputs are missing; set their paths in sample.json",
            )
        else:
            print("Running the sample...", flush=True)
            code, record = run_sample()
            if record is None:
                report.line(
                    "FAIL", "sample run", "immuknow stopped before recording the run"
                )
            else:
                produced = sum(
                    entry["original"]["status"] == "completed"
                    for entry in record["entries"]
                )
                report.line(
                    "OK" if code == 0 else "FAIL",
                    "sample run",
                    f"{record['status']}, {produced}/{len(record['entries'])} PDFs",
                )
                try:
                    findings = finding_summary(record)
                except (KeyError, TypeError, ValueError) as exc:
                    report.line("FAIL", "saved findings", str(exc))
                else:
                    for finding in findings:
                        print(f"        {finding}")
                    if findings:
                        print(
                            "      Run the sample to retain its CSV exports (see README)."
                        )

    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
