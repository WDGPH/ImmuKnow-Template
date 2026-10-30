"""Refuse files that may contain client information.

Only the synthetic sample in input/sample/ may be committed. The pre-commit hook
passes the files being committed; with no arguments, every tracked file is checked.

    uv run python scripts/check_client_data.py [paths...]

Uses only the standard library, so CI can run it before installing anything.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import PurePath

CLIENT_DATA = re.compile(
    r"\.(csv|xlsx?|xlsm|parquet|pdf|zip|log)$|(^|/)(run\.json|report\.html)$|^input/|(^|/)(runs|output)/",
    re.IGNORECASE,
)
SAMPLE = {"input/sample/sample_students.csv", "input/sample/sample_assignments.json"}


def client_data(paths: list[str]) -> list[str]:
    posix = (PurePath(path).as_posix() for path in paths)
    return [path for path in posix if CLIENT_DATA.search(path) and path not in SAMPLE]


def main(argv: list[str] | None = None) -> int:
    paths = sys.argv[1:] if argv is None else argv
    if not paths:
        paths = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True
        ).stdout.splitlines()
    found = client_data(paths)
    if found:
        print("These files may contain client information and must not be committed:")
        for path in found:
            print(f"  {path}")
        print("Keep cohort CSVs and assignments in input/ and runs in runs/.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
