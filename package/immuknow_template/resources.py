"""Read the packaged scaffold without modifying installed files."""

from __future__ import annotations

import hashlib
import json
import re
from importlib.resources import files
from pathlib import Path, PurePosixPath

PROVENANCE = "template-source.json"
REPOSITORY = "https://github.com/WDGPH/ImmuKnow-Template"


def safe_path(value: str) -> str:
    """Require one canonical project-relative file name."""
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or ":" in value
        or PurePosixPath(value).is_absolute()
        or any(part in {"", ".", ".."} for part in value.split("/"))
        or value.startswith("templates/lib/")
        or value == PROVENANCE
    ):
        raise ValueError(f"Unsafe scaffold path: {value!r}")
    return value


def resource_root() -> Path:
    """Return the installed, read-only scaffold directory."""
    return Path(str(files("immuknow_template").joinpath("data")))


def project_files(root: Path | None = None) -> dict[str, bytes]:
    """Verify the complete scaffold and return its files with source provenance."""
    root = resource_root() if root is None else root
    if root.is_symlink():
        raise ValueError("Template resources must not use linked paths")
    paths = list(root.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("Template resources must not use linked paths")
    provenance = (root / PROVENANCE).read_bytes()
    manifest = json.loads(provenance)
    if (
        manifest["repository"] != REPOSITORY
        or not isinstance(manifest["revision"], str)
        or not re.fullmatch(r"[0-9a-f]{40}", manifest["revision"])
    ):
        raise ValueError("Invalid Template source identity")
    hashes = manifest["files"]
    names = {safe_path(name) for name in hashes}
    actual = {path.relative_to(root).as_posix() for path in paths if path.is_file()}
    if actual != names | {PROVENANCE}:
        raise ValueError("Template resource files differ from the source manifest")
    result = {}
    for name, expected in hashes.items():
        data = (root / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Template resource hash differs: {name}")
        result[name] = data
    return result | {PROVENANCE: provenance}
