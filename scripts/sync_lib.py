"""Replace templates/lib/immuknow with the copy from the installed ImmuKnow.

Run after upgrading ImmuKnow. ImmuKnow refuses to render with a library that
differs from its own, so this directory is never edited by hand. Review the
change with `git diff templates/lib` before committing.

    uv run python scripts/sync_lib.py

The new copy is made and checked beside the project, then swapped in, so a
failed copy leaves the existing library in place.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from immuknow.component_resources import verify_components
from immuknow.resources import resource_root

from project import LIBRARY, ROOT, TEMPLATES_DIR


def main() -> int:
    target = TEMPLATES_DIR / LIBRARY
    try:
        verify_components(TEMPLATES_DIR)
    except ValueError:
        pass
    else:
        print(f"templates/{LIBRARY.as_posix()} already matches installed ImmuKnow.")
        return 0

    with tempfile.TemporaryDirectory(dir=ROOT, prefix=".sync-lib-") as staging:
        staged = Path(staging) / LIBRARY
        shutil.copytree(resource_root() / "templates" / LIBRARY, staged)
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

    print(
        f"Updated templates/{LIBRARY.as_posix()}. Review it with `git diff templates/lib`."
    )
    print(
        "Also compare settings.typ and the entry points with ImmuKnow's defaults in "
        f"{resource_root() / 'templates'}; those are yours to update."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
