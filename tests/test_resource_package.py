"""Installed resource wheels and source archives preserve the authored allowlist."""

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


def test_wheel_and_sdist_install_without_a_checkout_and_verify_their_files(tmp_path):
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    names = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["hatch"][
        "build"
    ]["targets"]["wheel"]["force-include"]
    # Build outside Git, without maintainer tests or generated Core resources.
    for name in names:
        target = checkout / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    shutil.copytree(ROOT / "src", checkout / "src")
    first = tmp_path / "first"
    run(["uv", "build", "--out-dir", str(first)], checkout)
    original = payload(next(first.glob("*.whl")))
    assert set(original) == set(names)
    assert not any(
        name.startswith(("templates/lib/", "tests/", "input/")) for name in original
    )
    for name in names:
        assert original[name] == (checkout / name).read_bytes()
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
    unpacked = tmp_path / "source"
    with tarfile.open(next(first.glob("*.tar.gz"))) as archive:
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
import json, shutil, tomllib
from pathlib import Path
from immuknow_template.resources import project_files, resource_root
files = project_files()
assert "templates/setup.typ" in files
assert "scripts/sync_lib.py" in files
project = tomllib.loads(files["pyproject.toml"].decode())
assert project["tool"]["uv"]["package"] is False
assert len(project["project"]["dependencies"]) == 1
assert project["project"]["dependencies"][0].startswith("ImmuKnow @ git+")
assert not any(name.startswith("templates/lib/") for name in files)
for name, data in files.items():
    path = Path("downloaded") / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
root = Path("copied-resources")
shutil.copytree(resource_root(), root)
changed = root / "templates/setup.typ"
changed.write_bytes(changed.read_bytes() + b"changed")
try:
    project_files(root)
except ValueError as error:
    assert "hash differs" in str(error)
else:
    raise AssertionError("Changed resource accepted")
changed.write_bytes(files["templates/setup.typ"])
(root / "extra").write_text("extra")
try:
    project_files(root)
except ValueError as error:
    assert "files differ" in str(error)
else:
    raise AssertionError("Extra resource accepted")
(root / "extra").unlink()
changed.unlink()
changed.symlink_to(resource_root() / "templates/setup.typ")
try:
    project_files(root)
except ValueError as error:
    assert "linked" in str(error)
else:
    raise AssertionError("Linked resource accepted")
assert json.loads(files["template-source.json"])["revision"] is None
print("Verified installed wheel")
"""
    result = run([str(python), "-I", "-c", code], tmp_path)
    assert result.stdout.strip() == "Verified installed wheel"
    downloaded = tmp_path / "downloaded"
    run(["uv", "sync", "--locked", "--no-default-groups"], downloaded)
    run(
        [
            "uv",
            "run",
            "--locked",
            "--no-default-groups",
            "python",
            "scripts/sync_lib.py",
        ],
        downloaded,
    )
    assert (downloaded / "templates/lib/immuknow").is_dir()
    assert not (checkout / "src/immuknow_template/data").exists()
