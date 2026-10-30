"""Fixed locations in this project. Every script resolves paths from here."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "runs"
SAMPLE_INPUT = ROOT / "input" / "sample" / "sample_students.csv"
SAMPLE_ASSIGNMENTS = ROOT / "input" / "sample" / "sample_assignments.json"
LIBRARY = Path("lib") / "immuknow"
