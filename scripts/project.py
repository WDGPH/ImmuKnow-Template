"""Fixed locations in this project. Every script resolves paths from here."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"
SAMPLE_INPUT = ROOT / "input" / "sample" / "rodent_dataset.csv"
SAMPLE_ASSIGNMENTS = ROOT / "input" / "sample" / "assignments.json"
LIBRARY = Path("lib") / "immuknow"
