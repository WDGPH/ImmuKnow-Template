"""Check that this machine and project are ready to run ImmuKnow.

Usage
-----
    uv run python scripts/check.py           # setup checks
    uv run python scripts/check.py --sample  # also run the sample end to end

Each setup check calls the same ImmuKnow function a run uses, so a result here
matches what a run would do: the run settings, the compiler, the shared Typst
library and the notice catalog. Missing fonts appear only when Typst compiles a
notice, so --sample reports them as compiler.font_substitution.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path

from immuknow.compile_notices import check_compiler
from immuknow.component_resources import verify_components
from immuknow.load_config import load_config
from immuknow.resources import rendering_build_info
from immuknow.version_notices import Language, load_catalog

import run
from project import CONFIG_DIR, LIBRARY, SAMPLE_ASSIGNMENTS, SAMPLE_INPUT, TEMPLATES_DIR


def typst_bin(config: dict) -> str:
    """Select the compiler with the expression ImmuKnow's orchestrator uses."""
    return os.environ.get("TYPST_BIN", config.get("typst", {}).get("bin", "typst"))


def catalog_entry_points(config_dir: Path, templates_dir: Path) -> dict[str, list[str]]:
    """Map each catalog version to the languages that have an entry point."""
    return {
        version: [
            language.value
            for language in Language
            if (templates_dir / f"{version}.{language.value}.typ").is_file()
        ]
        for version in load_catalog(config_dir).versions
    }


def run_sample() -> tuple[int, dict | None]:
    """Run the sample into a temporary directory and return its run record."""
    with tempfile.TemporaryDirectory() as output:
        code = run.main(
            [
                str(SAMPLE_INPUT),
                "--notice-assignments", str(SAMPLE_ASSIGNMENTS),
                "--output", output,
            ],
            quiet=True,
        )
        records = list(Path(output).glob("*/run.json"))
        record = json.loads(records[0].read_text(encoding="utf-8")) if records else None
    return code, record


def finding_summary(record: dict) -> list[str]:
    """One line per warning or failure code, counting the notices it affects."""
    notices: Counter[tuple[str, str]] = Counter()
    for entry in record["entries"]:
        for status, code in {
            (check["status"], check["code"])
            for check in entry["checks"]
            if check["status"] in ("warn", "fail")
        }:
            notices[status, code] += 1
    lines = [
        f"{status:<4}  {code}: {count} notice{'s' if count != 1 else ''}"
        for (status, code), count in sorted(
            notices.items(), key=lambda item: (item[0][0] != "fail", -item[1], item[0][1])
        )
    ]
    lines += [
        f"{check['status']:<4}  {check['code']}: {check['message']}"
        for check in record["checks"]
        if check["status"] in ("warn", "fail")
    ]
    return lines


class Report:
    def __init__(self) -> None:
        self.failed = False

    def line(self, status: str, label: str, detail: str = "") -> None:
        self.failed |= status == "FAIL"
        print(f"{status:<4}  {label}" + (f": {detail}" if detail else ""), flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check this ImmuKnow project.")
    parser.add_argument("--sample", action="store_true", help="also run the sample end to end")
    args = parser.parse_args(argv)
    report = Report()

    build = rendering_build_info()
    revision = (build["core_source_revision"] or "unknown")[:7]
    modified = " (with local changes)" if build["core_source_modified"] else ""
    report.line("OK", "ImmuKnow", f"{build['application_version']} at {revision}{modified}")

    config: dict = {}
    try:
        config = load_config(CONFIG_DIR / "parameters.yaml")
        report.line("OK", "config/parameters.yaml")
    except (OSError, ValueError) as exc:
        report.line("FAIL", "config/parameters.yaml", str(exc))

    # A diagnostic reports any compiler problem, including timeouts, rather than stopping.
    try:
        report.line("OK", "Typst", check_compiler(typst_bin(config)))
    except Exception as exc:
        report.line("FAIL", "Typst", str(exc))

    try:
        verify_components(TEMPLATES_DIR)
        report.line("OK", f"templates/{LIBRARY.as_posix()}", "matches installed ImmuKnow")
    except ValueError as exc:
        report.line(
            "FAIL",
            f"templates/{LIBRARY.as_posix()}",
            f"{exc} Run `uv run python scripts/sync_lib.py`.",
        )

    try:
        entry_points = catalog_entry_points(CONFIG_DIR, TEMPLATES_DIR)
    except (OSError, ValueError) as exc:
        report.line("FAIL", "config/notice_versions.yaml", str(exc))
        entry_points = {}
    for version, languages in entry_points.items():
        if languages:
            report.line("OK", f"notice {version}", ", ".join(languages))
        else:
            report.line("FAIL", f"notice {version}", f"no {version}.<language>.typ in templates/")

    if args.sample:
        if report.failed:
            report.line("SKIP", "sample run", "fix the failures above first")
        else:
            print("Running the sample...", flush=True)
            code, record = run_sample()
            if record is None:
                report.line("FAIL", "sample run", "immuknow stopped before recording the run")
            else:
                produced = sum(
                    entry["original"]["status"] == "completed" for entry in record["entries"]
                )
                report.line(
                    "OK" if code == 0 else "FAIL",
                    "sample run",
                    f"{record['status']}, {produced}/{len(record['entries'])} PDFs",
                )
                findings = finding_summary(record)
                for finding in findings:
                    print(f"        {finding}")
                if findings:
                    print(
                        "      For the full report, run the sample with scripts/run.py "
                        "(see README)."
                    )

    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
