"""Read the scaffold using standard wheel hashes and installation provenance."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import tomllib
from importlib.metadata import distribution
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
    """Verify the installed wheel's scaffold and return its files with provenance."""
    root = resource_root() if root is None else root
    paths = list(root.rglob("*"))
    if root.is_symlink() or any(path.is_symlink() for path in paths):
        raise ValueError("Template resources must not use linked paths")
    installed = distribution("immuknow-template-resources")
    prefix = "immuknow_template/data/"
    records = {
        safe_path(str(path).removeprefix(prefix)): path
        for path in installed.files or []
        if str(path).startswith(prefix) and path.suffix != ".pyc"
    }
    if not records:
        raise ValueError("Template wheel has no resource records")
    actual = {
        path.relative_to(root).as_posix()
        for path in paths
        if path.is_file()
        and not (
            "__pycache__" in path.relative_to(root).parts and path.suffix == ".pyc"
        )
    }
    if actual != set(records):
        raise ValueError("Template resource files differ from the wheel records")
    result = {}
    hashes = {}
    for name, record in records.items():
        data = (root / name).read_bytes()
        digest = hashlib.sha256(data).digest()
        expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        if (
            not record.hash
            or record.hash.mode != "sha256"
            or record.hash.value != expected
        ):
            raise ValueError(f"Template resource hash differs: {name}")
        result[name] = data
        hashes[name] = digest.hex()
    declared = tomllib.loads(result["pyproject.toml"].decode())["tool"]["hatch"][
        "build"
    ]["targets"]["wheel"]["force-include"]
    if declared != {name: prefix + name for name in records}:
        raise ValueError("Template resource files differ from the declared scaffold")
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
        "files": hashes,
    }
    return result | {
        PROVENANCE: (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode()
    }
