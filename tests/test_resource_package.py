"""Installed resource wheels and source archives preserve the authored allowlist."""

import json
import os
import subprocess
import sys
import tarfile
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
    first = tmp_path / "first"
    run(["uv", "build", "package", "--out-dir", str(first)], ROOT)
    original = payload(next(first.glob("*.whl")))
    names = json.loads((ROOT / "studio-scaffold.json").read_bytes())["files"]
    assert set(original) == set(names) | {"template-source.json"}
    assert not any(
        name.startswith(("templates/lib/", "tests/", "input/")) for name in original
    )
    for name in names:
        assert original[name] == (ROOT / name).read_bytes()
    assert not (ROOT / "package/immuknow_template/data").exists()
    stale = ROOT / "package/build/lib/immuknow_template/stale.py"
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text("Old build output must not ship")
    direct = tmp_path / "direct"
    run(["uv", "build", "package", "--wheel", "--out-dir", str(direct)], ROOT)
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
import json, shutil
from pathlib import Path
from immuknow_template.resources import project_files, resource_root
files = project_files()
assert "templates/setup.typ" in files
assert "scripts/sync_lib.py" in files
assert "build-system" not in files["pyproject.toml"].decode()
assert not any(name.startswith("templates/lib/") for name in files)
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
print(json.loads(files["template-source.json"])["revision"])
"""
    result = run([str(python), "-I", "-c", code], tmp_path)
    assert (
        result.stdout.strip()
        == json.loads(original["template-source.json"])["revision"]
    )
    assert not (ROOT / "package/immuknow_template/data").exists()
