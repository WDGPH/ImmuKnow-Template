"""Stage the authored allowlist in wheels and sdists without source-tree copies."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from immuknow_template.resources import PROVENANCE, REPOSITORY, project_files, safe_path  # noqa: E402


def scaffold() -> dict[str, bytes]:
    source = ROOT.parent
    allowlist = source / "studio-scaffold.json"
    if not allowlist.is_file():
        # A source archive carries the same verified payload and provenance.
        return project_files(ROOT / "immuknow_template/data")
    names = json.loads(allowlist.read_bytes())["files"]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate path in Template scaffold list")
    resources = {}
    for name in names:
        safe_path(name)
        path = source / name
        if any(parent.is_symlink() for parent in (path, *path.parents)):
            raise ValueError(f"Template source must not use linked paths: {name}")
        resources[name] = path.read_bytes()
    repository = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], cwd=source, text=True
    ).strip()
    if Path(repository).resolve() != source.resolve():
        raise ValueError(
            "Build Template resources from its Git checkout or source archive"
        )
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source, text=True
    ).strip()
    modified = bool(
        subprocess.check_output(
            [
                "git",
                "status",
                "--porcelain",
                "--",
                *names,
                "package",
                "studio-scaffold.json",
            ],
            cwd=source,
        )
    )
    manifest = {
        "repository": REPOSITORY,
        "revision": revision,
        "source_modified": modified,
        "files": {
            name: hashlib.sha256(data).hexdigest() for name, data in resources.items()
        },
    }
    return resources | {
        PROVENANCE: (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    }


def stage(target: Path, resources: dict[str, bytes] | None = None) -> None:
    if target.resolve().is_relative_to(ROOT / "immuknow_template"):
        raise ValueError("Build output must be separate from package source")
    if resources is None:
        resources = scaffold()
    if target.exists():
        shutil.rmtree(target)
    for name, data in resources.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    project_files(target)


class ResourceWheel(build_py):
    def run(self) -> None:
        target = Path(self.build_lib).resolve() / "immuknow_template"
        if target.is_relative_to(ROOT / "immuknow_template"):
            raise ValueError("Build output must be separate from package source")
        if target.exists():
            shutil.rmtree(target)
        super().run()
        stage(target / "data")


class ResourceSource(sdist):
    def make_release_tree(self, base_dir, files) -> None:
        # Capture provenance before setuptools creates an untracked release tree.
        resources = scaffold()
        super().make_release_tree(base_dir, files)
        stage(Path(base_dir).resolve() / "immuknow_template/data", resources)


setup(cmdclass={"build_py": ResourceWheel, "sdist": ResourceSource})
