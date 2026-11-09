"""Distributions include authored additions and support native project setup."""

import os
import shutil
import subprocess
import sys
import tarfile
import tomllib
import zipfile
from project import ROOT


def run(command, cwd):
    return subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)


def payload(wheel):
    with zipfile.ZipFile(wheel) as archive:
        prefix = "immuknow_template/data/"
        return {
            name.removeprefix(prefix): archive.read(name)
            for name in archive.namelist()
            if name.startswith(prefix) and not name.endswith("/")
        }


def test_wheel_and_sdist_include_authored_files_and_support_native_setup(tmp_path):
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    included = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["hatch"][
        "build"
    ]["only-include"]
    # Build outside Git, with generated files present to exercise exclusions.
    for name in included:
        target = checkout / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if (ROOT / name).is_dir():
            shutil.copytree(ROOT / name, target)
        else:
            shutil.copy2(ROOT / name, target)
    additions = {
        "templates/new_notice.typ": b"New starter",
        "templates/translations/new.json": b"{}",
        "config/new.json": b"{}",
    }
    excluded = {
        "scripts/new_helper.py": b"# Maintainer helper\n",
        "templates/lib/immuknow/generated.typ": b"Generated Core",
        "templates/__pycache__/cached.pyc": b"Cache",
        "scripts/__pycache__/cached.pyc": b"Cache",
        "scripts/cached.pyc": b"Cache",
        "tests/not_distributed.py": b"Maintainer test",
        "input/not_distributed.csv": b"Fictional input",
        "unrelated.txt": b"Unrelated root file",
    }
    for name, data in (additions | excluded).items():
        path = checkout / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    first = tmp_path / "first"
    run(["uv", "build", "--out-dir", str(first)], checkout)
    original = payload(next(first.glob("*.whl")))
    assert additions.items() <= original.items()
    assert not set(excluded).intersection(original)
    assert {
        "templates/settings.typ",
        "core-revision.txt",
        "README.md",
    } <= set(original)
    assert not any(
        name.startswith(("templates/lib/", "tests/", "input/")) for name in original
    )
    for name, data in original.items():
        assert data == (checkout / name).read_bytes()
    assert not (checkout / "src/immuknow_template/data").exists()
    stale = checkout / "build/lib/immuknow_template/stale.py"
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text("Old build output must not ship")
    direct = tmp_path / "direct"
    run(["uv", "build", "--wheel", "--out-dir", str(direct)], checkout)
    direct_wheel = next(direct.glob("*.whl"))
    assert payload(direct_wheel) == original
    with zipfile.ZipFile(direct_wheel) as archive:
        assert "immuknow_template/stale.py" not in archive.namelist()
        assert (
            archive.read("immuknow_template/examples/assignments.json")
            == (checkout / "input/sample/sample_assignments.json").read_bytes()
        )
        assert (
            archive.read("immuknow_template/examples/clients.csv")
            == (checkout / "input/sample/sample_students.csv").read_bytes()
        )
    unpacked = tmp_path / "source"
    with tarfile.open(next(first.glob("*.tar.gz"))) as archive:
        archived = {name.split("/", 1)[1] for name in archive.getnames() if "/" in name}
        assert set(additions) <= archived
        assert not (set(excluded) - {"scripts/new_helper.py"}).intersection(archived)
        archive.extractall(unpacked, filter="data")
    (source,) = unpacked.iterdir()
    rebuilt = tmp_path / "rebuilt"
    run(["uv", "build", "--wheel", "--out-dir", str(rebuilt)], source)
    wheel = next(rebuilt.glob("*.whl"))
    assert payload(wheel) == original
    environment = tmp_path / "environment"
    run(["uv", "venv", "--python", sys.executable, str(environment)], tmp_path)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(python),
            "--offline",
            "--no-deps",
            "--compile-bytecode",
            str(wheel),
        ],
        tmp_path,
    )
    code = """
import json, tomllib
from pathlib import Path
from immuknow_template.resources import example_assignments_path, example_clients_path, project_files
example = example_clients_path()
assert example.is_file()
assert example.read_bytes() == Path("checkout/input/sample/sample_students.csv").read_bytes()
assignments = example_assignments_path()
assert assignments.read_bytes() == Path("checkout/input/sample/sample_assignments.json").read_bytes()
import csv
with example.open(newline="", encoding="utf-8-sig") as stream:
    clients = {row["client_id"] for row in csv.DictReader(stream)}
assigned = [row["client_id"] for row in json.loads(assignments.read_text())]
assert len(assigned) == len(set(assigned)) and set(assigned) == clients
files = project_files()
assert "input/sample/sample_students.csv" not in files
assert "input/sample/sample_assignments.json" not in files
assert "templates/settings.typ" in files
assert "templates/setup.typ" not in files
assert "templates/presentation.typ" not in files
for language in ("en", "fr"):
    for kind in ("chart", "overdue"):
        assert f"templates/translations/{language}_diseases_{kind}.json" in files
assert not any(name.startswith("scripts/") for name in files)
assert not {"pyproject.toml", "uv.lock", ".python-version", ".pre-commit-config.yaml"}.intersection(files)
assert "core-revision.txt" in files
assert "README.md" in files
assert "references/ontario_schools.json" in files
assert not any(name.startswith("templates/lib/") for name in files)
for name, data in files.items():
    path = Path("downloaded") / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
assert "templates/new_notice.typ" in files
assert "config/new.json" in files
assert not any("__pycache__" in name or name.endswith(".pyc") for name in files)
assert json.loads(files["template-source.json"])["revision"] is None
print("Read installed wheel")
"""
    result = run([str(python), "-I", "-c", code], tmp_path)
    assert result.stdout.strip() == "Read installed wheel"
    downloaded = tmp_path / "downloaded"
    binary = os.environ.get("IMMUKNOW_BIN") or shutil.which("immuknow")
    assert binary, "Install standalone Core or set IMMUKNOW_BIN"
    # No Python environment or tools are installed in the exported project.
    result = subprocess.run(
        [binary, "project", "sync"],
        cwd=downloaded,
        env={**os.environ, "PATH": ""},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (downloaded / "templates/lib/immuknow").is_dir()
    assert not (downloaded / ".venv").exists()
    assert not (checkout / "src/immuknow_template/data").exists()
