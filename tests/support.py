"""Paths and native command execution shared by project tests."""

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
TEMPLATES_DIR = ROOT / "templates"
SAMPLE_INPUT = ROOT / "input/sample/sample_students.csv"
SAMPLE_ASSIGNMENTS = ROOT / "input/sample/sample_assignments.json"


def native(*arguments):
    binary = os.environ.get("IMMUKNOW_BIN") or shutil.which("immuknow")
    if not binary:
        raise RuntimeError("Install standalone Core or set IMMUKNOW_BIN")
    return subprocess.run(
        [binary, *arguments], cwd=ROOT, capture_output=True, text=True
    )
