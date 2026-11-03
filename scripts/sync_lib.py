"""Generate the shared library from installed Core; explicitly refresh it on upgrade."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from immuknow.component_resources import verify_components
from immuknow.resources import typst_library_root

from project import LIBRARY, TEMPLATES_DIR


def ensure_library(templates: Path, *, replace: bool = False) -> None:
    """Generate a missing library, retaining an existing mismatched tree for review."""
    target = templates / LIBRARY
    if not templates.is_dir():
        raise ValueError(f"Template directory does not exist: {templates}")
    if (templates / "lib").is_symlink() or target.is_symlink():
        raise ValueError("The supplied ImmuKnow library must not use linked paths.")
    if target.exists():
        try:
            verify_components(templates)
        except ValueError:
            if not replace:
                raise
        else:
            return
    with tempfile.TemporaryDirectory(
        dir=templates.parent, prefix=".sync-lib-"
    ) as staging:
        staged = Path(staging) / LIBRARY
        shutil.copytree(typst_library_root(), staged)
        verify_components(Path(staging))
        previous = Path(staging) / "previous"
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
    ensure_library(TEMPLATES_DIR, replace=True)
    print(f"templates/{LIBRARY.as_posix()} matches installed ImmuKnow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
