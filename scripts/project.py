"""Project directories and sample paths used by the helper scripts."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "runs"


def sample_paths() -> tuple[Path, Path]:
    """Read project-relative sample paths; Studio supplies its selected example."""
    selection = ROOT / "sample.json"
    sample = (
        json.loads(selection.read_text(encoding="utf-8"))
        if selection.is_file()
        else {
            "csv": "input/sample/sample_students.csv",
            "assignments": "input/sample/sample_assignments.json",
        }
    )
    if not isinstance(sample, dict) or set(sample) != {"csv", "assignments"}:
        raise ValueError("sample.json must contain csv and assignments paths")
    paths = []
    for key in ("csv", "assignments"):
        value = sample[key]
        if (
            not isinstance(value, str)
            or not value
            or "\\" in value
            or Path(value).is_absolute()
            or ".." in Path(value).parts
        ):
            raise ValueError(
                f"sample.json {key} must be a relative path inside the project"
            )
        paths.append(ROOT / value)
    return paths[0], paths[1]


SAMPLE_INPUT, SAMPLE_ASSIGNMENTS = sample_paths()
LIBRARY = Path("lib") / "immuknow"
