"""Run the immuknow command with this project's config/, templates/ and runs/.

Usage
-----
    uv run python scripts/run.py input/students.csv --notice-assignments input/assignments.json
    uv run python scripts/run.py input/students.csv --template overdue_diseases_v1.en.typ

Relative paths start from your working directory, as with immuknow itself. A
--template given as a bare file name is a file in templates/, as in an
assignments file. --config, --templates and --output default to this project's
directories. Any other option, such as --input-encoding cp1252, is passed to
immuknow unchanged.

The exit code is immuknow's: 0 when every notice was produced (warnings may
still need review before delivery), 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from project import CONFIG_DIR, OUTPUT_DIR, TEMPLATES_DIR


def parse_args(argv: list[str] | None = None) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run immuknow with this project's directories.",
        epilog="Other options are passed to immuknow; see `uv run immuknow --help`.",
        allow_abbrev=False,
    )
    parser.add_argument("input_file", type=Path, help="Cohort CSV")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--notice-assignments",
        type=Path,
        help="JSON assignments: client_id and template filename for each client",
    )
    selection.add_argument(
        "--template",
        type=Path,
        dest="notice_template",
        help="One <version_id>.<language>.typ file for every client; "
        "a bare file name is looked up in templates/",
    )
    parser.add_argument("--config", type=Path, dest="config_dir", default=CONFIG_DIR)
    parser.add_argument(
        "--templates",
        type=Path,
        dest="template_dir",
        help=f"Template directory for --notice-assignments (default: {TEMPLATES_DIR})",
    )
    parser.add_argument("--output", type=Path, dest="output_dir", default=OUTPUT_DIR)
    args, passthrough = parser.parse_known_args(argv)
    if args.notice_template:
        if args.template_dir:
            parser.error("--templates cannot be used with --template; use the template's folder")
        if len(args.notice_template.parts) == 1:
            args.notice_template = TEMPLATES_DIR / args.notice_template
    elif args.template_dir is None:
        args.template_dir = TEMPLATES_DIR
    return args, passthrough


def immuknow_command() -> str:
    """Prefer the immuknow installed beside this Python, as `uv run` provides."""
    scripts = Path(sys.executable).parent
    found = shutil.which("immuknow", path=str(scripts)) or shutil.which("immuknow")
    if found is None:
        raise RuntimeError("The immuknow command is not installed. Run `uv sync`.")
    return found


def run_ids(output_dir: Path) -> set[str]:
    if not output_dir.is_dir():
        return set()
    return {path.name for path in output_dir.iterdir() if (path / "run.json").is_file()}


def print_outcome(run_dir: Path) -> None:
    """Say where the run's report is and what to do next."""
    try:
        status = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))["status"]
    except (OSError, ValueError, KeyError) as exc:
        print(
            f"Could not read the run record {run_dir / 'run.json'} ({exc}). "
            f"Look in {run_dir} for what the run left.",
            file=sys.stderr,
        )
        return
    print(f"Run status: {status}\nReport: {run_dir / 'report.html'}")
    if status == "completed_with_warnings":
        print(
            "Some notices have warnings and are held for review. Open the report, "
            "then release reviewed notices with:\n"
            f"  uv run immuknow-rebundle {run_dir} --accept-warning <token> "
            '--reason "<why it is acceptable>"'
        )
    elif status != "completed":
        print("Open the report to see which rows or notices failed and why.")


def main(argv: list[str] | None = None, *, quiet: bool = False) -> int:
    """Run immuknow; quiet captures its output unless no run record explains the result."""
    args, passthrough = parse_args(argv)
    try:
        command = [immuknow_command(), str(args.input_file)]
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.notice_template:
        command += ["--template", str(args.notice_template)]
    else:
        command += [
            "--notice-assignments", str(args.notice_assignments),
            "--templates", str(args.template_dir),
        ]
    command += ["--config", str(args.config_dir), "--output", str(args.output_dir)]
    command += passthrough

    before = run_ids(args.output_dir)
    result = subprocess.run(command, capture_output=quiet, text=True)
    new_runs = sorted(run_ids(args.output_dir) - before)
    if quiet:
        if not new_runs:
            print(result.stdout + result.stderr, end="", file=sys.stderr)
        return result.returncode
    if new_runs:
        print_outcome(args.output_dir / new_runs[-1])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
