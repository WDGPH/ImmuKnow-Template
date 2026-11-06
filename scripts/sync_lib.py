"""Export Core's shared Typst library into the authored project."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from project import LIBRARY, TEMPLATES_DIR, immuknow_command


def library_files(root: Path) -> dict[str, bytes]:
    """Read a tree without following links, for exact resource comparison."""
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"Shared library is missing or linked: {root}")
    files = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Shared library must not contain linked paths: {path}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path.read_bytes()
        elif not path.is_dir():
            raise ValueError(f"Unsupported shared library path: {path}")
    return files


def ensure_library(templates: Path, *, replace: bool = False) -> None:
    """Install a missing library; replace a changed one only when requested."""
    target = templates / LIBRARY
    if not templates.is_dir():
        raise ValueError(f"Template directory does not exist: {templates}")
    if (templates / "lib").is_symlink() or target.is_symlink():
        raise ValueError("The supplied ImmuKnow library must not use linked paths.")
    if (templates / "lib").exists() and not (templates / "lib").is_dir():
        raise ValueError("The template lib path must be a directory")
    with tempfile.TemporaryDirectory(
        dir=templates.parent, prefix=".sync-lib-"
    ) as staging:
        staging = Path(staging)
        result = subprocess.run(
            [immuknow_command(), "resources", "--output", str(staging / "resources")],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise ValueError(
                f"Could not export ImmuKnow resources: {result.stderr.strip()}"
            )
        source = staging / "resources" / "typst"
        exported = library_files(source)
        if target.exists():
            current = library_files(target)
            if current == exported:
                return
            if not replace:
                raise ValueError(
                    "Shared ImmuKnow library differs; run scripts/sync_lib.py to refresh it."
                )
        staged = staging / "replacement"
        shutil.copytree(source, staged)
        previous = staging / "previous"
        if target.exists():
            target.rename(previous)
        target.parent.mkdir(exist_ok=True)
        try:
            staged.rename(target)
        except OSError:
            if previous.exists():
                previous.rename(target)
            raise


def main() -> int:
    try:
        ensure_library(TEMPLATES_DIR, replace=True)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"templates/{LIBRARY.as_posix()} matches installed ImmuKnow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
