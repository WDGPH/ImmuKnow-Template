"""Read packaged starter files and describe their installation provenance."""

from __future__ import annotations

import hashlib
import json
import re
from importlib.metadata import distribution
from importlib.resources import files
from pathlib import Path

PROVENANCE = "template-source.json"
REPOSITORY = "https://github.com/WDGPH/ImmuKnow-Template"


def resource_root() -> Path:
    """Return the installed, read-only scaffold directory."""
    return Path(str(files("immuknow_template").joinpath("data")))


def example_clients_path() -> Path:
    """Return the packaged fictional source CSV used for notice previews."""
    return Path(str(files("immuknow_template").joinpath("examples/clients.csv")))


def example_assignments_path() -> Path:
    """Return the packaged default notice choices for the fictional clients."""
    return Path(str(files("immuknow_template").joinpath("examples/assignments.json")))


def project_files() -> dict[str, bytes]:
    """Return the installed starter files and export provenance."""
    root = resource_root()
    result = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    }
    installed = distribution("immuknow-template-resources")
    origin = json.loads(installed.read_text("direct_url.json") or "{}")
    revision = origin.get("vcs_info", {}).get("commit_id")
    if revision and (
        origin.get("url", "").removesuffix(".git") != REPOSITORY
        or not re.fullmatch(r"[0-9a-f]{40}", revision)
    ):
        raise ValueError("Invalid Template source identity")
    provenance = {
        "repository": REPOSITORY,
        "revision": revision,
        "source_modified": False if revision else None,
        "files": {
            name: hashlib.sha256(data).hexdigest() for name, data in result.items()
        },
    }
    return result | {
        PROVENANCE: (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode()
    }
